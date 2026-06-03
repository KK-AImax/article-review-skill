import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skill" / "article-review-skill" / "scripts" / "audit_article.py"


def load_module():
    spec = importlib.util.spec_from_file_location("audit_article", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AuditArticleTest(unittest.TestCase):
    def test_privacy_and_structure_issues_are_detected(self):
        module = load_module()
        result = module.audit(
            """# Draft

In this article, we will discuss a confidential roadmap.

## One

Use [learn more](https://example.com).
"""
        )

        messages = " ".join(issue["message"] for issue in result["issues"])
        self.assertIn(result["decision"], {"Needs revision before publishing", "Hold"})
        self.assertIn("confidential", messages)
        self.assertIn("Fewer than 3 H2", messages)
        self.assertEqual(result["metrics"]["bad_anchor_links"], 1)


    def test_publish_ready_shape_scores_well(self):
        module = load_module()
        result = module.audit(
            """# Choosing A Documentation Platform

Choose a documentation platform by comparing permissions, search quality, integrations, review workflows, and total ownership cost. Small teams usually need quick setup, while larger teams need governance and analytics.

## Compare Core Requirements

| Requirement | Small Team | Larger Team |
|---|---|---|
| Setup time | 1 week | 4 weeks |
| Review workflow | Lightweight | Required |

## Check Integration Needs

Teams should list the 5 systems that must connect before they choose a platform.

## Review Governance Risk

Confirm permissions, audit logs, and ownership before migrating more than 100 pages.

## What should teams compare first?

Compare search, permissions, integrations, and maintenance effort first.

## How long does migration take?

Most teams should estimate 2 to 6 weeks depending on content volume.

## Which option is best for small teams?

Small teams usually benefit from simple editing, fast onboarding, and low administration overhead.
"""
        )

        self.assertGreaterEqual(result["score"], 85)
        self.assertEqual(result["decision"], "Publish-ready")


if __name__ == "__main__":
    unittest.main()
