#!/usr/bin/env python3
import unittest

from tools import github_ci_status as ci


def workflow_block(name: str, run_id: int, status: str) -> str:
    icon = {
        "success": '<svg aria-label="This job succeeded"></svg>',
        "failed": '<svg aria-label="This job failed"></svg>',
        "running": '<svg aria-label="currently running"></svg>',
    }[status]
    return (
        f'<a href="/{ci.REPOSITORY}/actions/runs/{run_id}"><span>{name}</span></a>'
        f"{icon}"
    )


def current_workflow_block(name: str, run_id: int, label: str) -> str:
    return (
        f'<a href="/{ci.REPOSITORY}/actions/runs/{run_id}"><span>{name}</span></a>'
        f'<svg aria-label="{label}"></svg>'
    )


class GitHubCiStatusTest(unittest.TestCase):
    def test_required_successful_workflows_pass(self):
        raw = "".join(
            workflow_block(name, index + 100, "success")
            for index, name in enumerate(ci.REQUIRED_WORKFLOWS)
        )
        workflows = ci.parse_workflows(raw)
        self.assertEqual(ci.workflow_issues(workflows), [])
        self.assertTrue(all(workflows[name]["succeeded"] for name in ci.REQUIRED_WORKFLOWS))

    def test_shared_pending_template_after_success_does_not_override_job_result(self):
        raw = workflow_block(ci.REQUIRED_WORKFLOWS[0], 100, "success") + '<template aria-label="In progress"></template>'
        workflows = ci.parse_workflows(raw)
        self.assertTrue(workflows[ci.REQUIRED_WORKFLOWS[0]]["succeeded"])
        self.assertFalse(workflows[ci.REQUIRED_WORKFLOWS[0]]["pending"])

    def test_current_completed_successfully_label_passes(self):
        raw = current_workflow_block(ci.REQUIRED_WORKFLOWS[0], 101, "completed successfully: ")
        workflows = ci.parse_workflows(raw)
        self.assertEqual(ci.workflow_issues(workflows), [])
        self.assertTrue(workflows[ci.REQUIRED_WORKFLOWS[0]]["succeeded"])

    def test_current_completed_with_failure_label_fails(self):
        raw = current_workflow_block(ci.REQUIRED_WORKFLOWS[0], 102, "completed with failure: ")
        workflows = ci.parse_workflows(raw)
        self.assertFalse(workflows[ci.REQUIRED_WORKFLOWS[0]]["succeeded"])

    def test_failed_workflow_is_rejected(self):
        raw = workflow_block(ci.REQUIRED_WORKFLOWS[0], 100, "failed")
        workflows = ci.parse_workflows(raw)
        issues = ci.workflow_issues(workflows)
        self.assertIn(
            f"required GitHub workflow is not successful: {ci.REQUIRED_WORKFLOWS[0]}",
            issues,
        )

    def test_running_workflow_is_rejected(self):
        raw = workflow_block(ci.REQUIRED_WORKFLOWS[0], 100, "running")
        workflows = ci.parse_workflows(raw)
        self.assertFalse(workflows[ci.REQUIRED_WORKFLOWS[0]]["succeeded"])
        self.assertEqual(workflows[ci.REQUIRED_WORKFLOWS[0]]["pending"], True)


if __name__ == "__main__":
    unittest.main()
