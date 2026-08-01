#!/usr/bin/env python3
import unittest

from tools import adsense_final_review_packet as packet


class AdSenseFinalReviewPacketTest(unittest.TestCase):
    def passing_checks(self):
        checks = []
        for spec in packet.CHECKS:
            metrics = {"adsense_submission_ready": "true"} if spec.name == "submission_gate" else {}
            checks.append({"name": spec.name, "status": "passed", "metrics": metrics})
        return checks

    def test_required_check_set_covers_every_review_surface(self):
        self.assertEqual(
            {spec.name for spec in packet.CHECKS},
            {
                "submission_gate",
                "github_ci",
                "local_review_surface",
                "public_review_surface",
                "public_support_sync",
                "public_editorial_trust",
                "public_indexability",
                "public_headers",
                "public_assets",
                "public_internal_links",
                "public_schema",
                "public_schema_urls",
                "public_external_links",
                "public_runtime_performance",
                "public_not_found",
                "public_visual",
            },
        )
        self.assertTrue(all("submit" not in packet.command_text(spec.command).lower() for spec in packet.CHECKS))

    def test_all_checks_and_repository_must_pass(self):
        summary = packet.summarize(
            self.passing_checks(),
            {"clean": True, "headMatchesOriginMain": True},
        )
        self.assertTrue(summary["readyToSubmit"])
        self.assertEqual(summary["blockedReasons"], [])

    def test_failed_gate_blocks_packet(self):
        checks = self.passing_checks()
        checks[0] = {
            "name": "submission_gate",
            "status": "failed",
            "metrics": {"adsense_submission_ready": "false"},
        }
        summary = packet.summarize(checks, {"clean": True, "headMatchesOriginMain": True})
        self.assertFalse(summary["readyToSubmit"])
        self.assertEqual(summary["failedChecks"], 1)
        self.assertIn("check failed: submission_gate", summary["blockedReasons"])
        self.assertIn("AdSense submission gate is not ready", summary["blockedReasons"])

    def test_skipped_visual_or_dirty_repository_blocks_packet(self):
        checks = self.passing_checks()
        checks[-1] = {"name": "public_visual", "status": "skipped", "metrics": {}}
        summary = packet.summarize(checks, {"clean": False, "headMatchesOriginMain": True})
        self.assertFalse(summary["readyToSubmit"])
        self.assertEqual(summary["skippedChecks"], 1)
        self.assertFalse(summary["repositoryClean"])
        self.assertIn("check skipped: public_visual", summary["blockedReasons"])
        self.assertIn("repository has uncommitted changes", summary["blockedReasons"])

    def test_metrics_parser_ignores_narrative_output(self):
        self.assertEqual(
            packet.parse_metrics("heading\nadsense_submission_ready=false\n- pending: wait\n"),
            {"adsense_submission_ready": "false"},
        )


if __name__ == "__main__":
    unittest.main()
