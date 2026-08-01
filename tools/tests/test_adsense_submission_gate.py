#!/usr/bin/env python3
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

from tools import adsense_submission_gate as gate


class AdSenseSubmissionGateTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.root_patch = patch.object(gate, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.addCleanup(self.temp_dir.cleanup)

        self.gsc_path = self.write_json(
            "evidence/gsc.json",
            {
                "latestMaterialDeployment": {
                    "commit": "material-commit",
                    "commitCreatedAt": "2026-08-01T21:14:42+08:00",
                    "cloudflareDeployment": "deployment-id",
                    "productionVerifiedAt": "2026-08-01T13:16:33Z",
                }
            },
        )
        self.production_path = self.write_json(
            "evidence/production.json",
            {
                "checkedAt": "2026-08-01T13:16:33Z",
                "reviewSurfaceCommit": "material-commit",
                "cloudflareDeployment": {"id": "deployment-id"},
                "productionChecks": {"issues": 0},
                "result": "pass",
            },
        )
        self.adsense_path = self.write_json(
            "evidence/adsense.json",
            {"dashboard": {"reviewSubmitted": False}},
        )
        self.state = self.base_state()

    def write_json(self, relative_path: str, payload: dict) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def gate_item(self, evidence: Path) -> dict:
        return {
            "confirmed": False,
            "checkedAt": "2026-08-01T13:24:44Z",
            "evidence": str(evidence.relative_to(self.root)),
        }

    def base_state(self) -> dict:
        gates = {name: self.gate_item(self.gsc_path) for name in gate.GSC_GATES}
        gates.update({name: self.gate_item(self.adsense_path) for name in gate.ADSENSE_GATES})
        gates["gscPagesWithImpressions"].update({"value": 0, "minimum": 5})
        gates["productionAuditGreen"] = self.gate_item(self.production_path)
        return {
            "schemaVersion": 1,
            "site": "https://lovetypes.tw/",
            "lastMaterialChange": "2026-08-01",
            "minimumStableDays": 14,
            "maximumEvidenceAgeDays": 3,
            "reviewSubmitted": False,
            "externalGates": gates,
        }

    def test_consistent_evidence_contract_is_valid(self):
        self.assertEqual(gate.state_validation_issues(self.state), [])

    def test_material_commit_mismatch_is_rejected(self):
        production = json.loads(self.production_path.read_text(encoding="utf-8"))
        production["reviewSurfaceCommit"] = "different-commit"
        self.production_path.write_text(json.dumps(production), encoding="utf-8")
        self.assertIn(
            "GSC and production evidence disagree on the material commit",
            gate.state_validation_issues(self.state),
        )

    def test_mixed_gsc_snapshots_are_rejected(self):
        second_gsc = self.write_json("evidence/gsc-second.json", {})
        self.state["externalGates"]["sitemapAccepted"]["evidence"] = str(second_gsc.relative_to(self.root))
        self.assertIn("GSC gates must share one evidence snapshot", gate.state_validation_issues(self.state))

    def test_stale_and_future_evidence_are_rejected(self):
        item = {"checkedAt": "2026-08-01T13:24:44Z"}
        self.assertIsNone(gate.evidence_freshness_issue("example", item, date(2026, 8, 4), 3))
        self.assertEqual(
            gate.evidence_freshness_issue("example", item, date(2026, 8, 5), 3),
            "external evidence is stale: example age=4d max=3d",
        )
        self.assertEqual(
            gate.evidence_freshness_issue("example", item, date(2026, 7, 31), 3),
            "external evidence observation is in the future: example",
        )

    def test_report_only_keeps_expected_pending_gates_non_failing(self):
        output = io.StringIO()
        with redirect_stdout(output):
            status = gate.report_only(
                self.state,
                date(2026, 8, 1),
                Path("config/adsense-submission-gate.json"),
                [],
            )
        self.assertEqual(status, 0)
        self.assertIn("adsense_submission_pending_conditions=9", output.getvalue())
        self.assertIn("adsense_submission_evidence_refresh_due=0", output.getvalue())
        self.assertIn("adsense_submission_ready=false", output.getvalue())
        self.assertIn("adsense_review_submitted=false", output.getvalue())

    def test_report_only_fails_invalid_evidence_contract(self):
        output = io.StringIO()
        with redirect_stdout(output):
            status = gate.report_only(
                self.state,
                date(2026, 8, 1),
                Path("config/adsense-submission-gate.json"),
                ["invalid evidence"],
            )
        self.assertEqual(status, 1)
        self.assertIn("adsense_submission_validation_issues=1", output.getvalue())

    def test_report_only_handles_invalid_gate_shape_without_crashing(self):
        self.state["externalGates"] = None
        validation_issues = gate.state_validation_issues(self.state)
        output = io.StringIO()
        with redirect_stdout(output):
            status = gate.report_only(
                self.state,
                date(2026, 8, 1),
                Path("config/adsense-submission-gate.json"),
                validation_issues,
            )
        self.assertEqual(status, 1)
        self.assertIn("adsense_submission_validation_issues=1", output.getvalue())

    def test_report_only_flags_each_stale_evidence_snapshot_once(self):
        output = io.StringIO()
        with redirect_stdout(output):
            status = gate.report_only(
                self.state,
                date(2026, 8, 5),
                Path("config/adsense-submission-gate.json"),
                [],
            )
        self.assertEqual(status, 0)
        self.assertIn("adsense_submission_evidence_refresh_due=3", output.getvalue())
        self.assertEqual(output.getvalue().count("- refresh:"), 3)


if __name__ == "__main__":
    unittest.main()
