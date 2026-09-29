import unittest
from unittest.mock import patch

from engine import process_return


class ReturnWorkflowTests(unittest.TestCase):
    def test_normal_order_gets_mock_refund(self):
        result = process_return("ORD-1001", "Damaged item")
        self.assertEqual(result["decision"], "auto_refund")
        self.assertEqual(result["refund"]["reference"], "DEMO-ORD-1001")
        self.assertEqual(result["risk"]["score"], 0)

    def test_high_risk_order_waits_for_human(self):
        result = process_return("ORD-2005", "Wrong item")
        self.assertEqual(result["decision"], "review_required")
        self.assertEqual(result["risk"]["score"], 100)
        self.assertNotIn("refund", result)

    def test_expired_order_stops_before_risk_check(self):
        result = process_return("ORD-3001", "Changed my mind")
        self.assertEqual(result["decision"], "ineligible")
        self.assertNotIn("risk", result)

    def test_unknown_order_fails_cleanly(self):
        result = process_return("missing", "Other")
        self.assertEqual(result["decision"], "not_found")
        self.assertEqual(len(result["trace"]), 1)

    def test_digital_item_is_ineligible(self):
        result = process_return("ORD-4001", "Other")
        self.assertEqual(result["decision"], "ineligible")
        self.assertIn("Digital", result["eligibility"]["reason"])

    def test_ai_investigates_but_cannot_override_high_risk_gate(self):
        class FakeMessage:
            def __init__(self, content, tool_calls=None):
                self.content = content
                self.tool_calls = tool_calls or []

        class FakeAgent:
            def invoke(self, *_args, **_kwargs):
                return {"messages": [
                    FakeMessage("", [{"name": "lookup_order"}]),
                    FakeMessage("Looks acceptable for an automatic refund."),
                ]}

        with patch("engine.ChatOpenRouter"), patch("engine.create_agent", return_value=FakeAgent()):
            result = process_return(
                "ORD-2005", "Wrong item", openrouter_api_key="test-key"
            )
        self.assertEqual(result["ai_status"], "connected")
        self.assertEqual(result["ai_tool_calls"], ["lookup_order"])
        self.assertEqual(result["decision"], "review_required")
        self.assertNotIn("refund", result)
        self.assertNotIn("test-key", str(result))

    def test_ai_failure_keeps_policy_workflow_available(self):
        with patch("engine.ChatOpenRouter", side_effect=RuntimeError("model unavailable")):
            result = process_return(
                "ORD-1001", "Damaged item", openrouter_api_key="test-key"
            )
        self.assertEqual(result["ai_status"], "error")
        self.assertEqual(result["decision"], "auto_refund")


if __name__ == "__main__":
    unittest.main()
