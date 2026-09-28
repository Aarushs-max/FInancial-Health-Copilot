"""
API & Intelligence Integration Tests for Financial Health Copilot.
Tests FastAPI controller handlers directly, including Chatbot and Multilingual engines.
"""

import unittest
from app.main import (
    health_check, get_personas, get_profile, check_affordability,
    check_cashflow_guard, get_projections, get_explainability,
    get_copilot_narrative, add_manual_transaction, initiate_aa_flow,
    verify_aa_otp, chat_with_copilot, get_translations
)
from app.models.schemas import ManualExpenseInput, AAConsentRequest, ExpenseCategory, ChatRequest


class TestCopilotDirectHandlers(unittest.TestCase):
    def test_health_check(self):
        res = health_check()
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["app"], "Financial Health Copilot")

    def test_get_personas(self):
        personas = get_personas()
        self.assertEqual(len(personas), 3)
        ids = [p["id"] for p in personas]
        self.assertIn("rohan", ids)
        self.assertIn("priya", ids)
        self.assertIn("amit", ids)

    def test_get_profile_rohan(self):
        profile = get_profile("rohan")
        self.assertEqual(profile.name, "Rohan Mehta")
        self.assertEqual(profile.monthly_income, 125000.0)

    def test_check_affordability_rohan(self):
        res = check_affordability(user_id="rohan", investment_amount=15000.0)
        self.assertEqual(res.risk_status, "CRITICAL")
        self.assertIn("Exceeds Available Disposable Income", res.headline_verdict)

    def test_check_affordability_priya(self):
        res = check_affordability(user_id="priya", investment_amount=5000.0)
        self.assertEqual(res.risk_status, "SAFE")
        self.assertTrue(res.remaining_disposable_buffer > 15000)

    def test_cashflow_guard_amit(self):
        res = check_cashflow_guard(user_id="amit", reference_day=28)
        self.assertTrue(res.has_cashflow_warning)
        self.assertGreater(res.projected_shortfall, 10000.0)
        self.assertGreater(len(res.driving_obligations), 0)

    def test_projections_calculation(self):
        res = get_projections(investment_amount=5000.0)
        self.assertEqual(len(res.scenarios), 4)
        self.assertEqual(len(res.chart_labels), 4)
        self.assertGreater(res.sip_series[-1], res.cash_series[-1])

    def test_explainability_audit(self):
        items = get_explainability(user_id="rohan", investment_amount=5000.0)
        self.assertGreaterEqual(len(items), 3)
        types = [item.type for item in items]
        self.assertIn("OBSERVED_FACT", types)
        self.assertIn("MODEL_PREDICTION", types)
        self.assertIn("ACTIONABLE_RECOMMENDATION", types)

    def test_copilot_narrative(self):
        res = get_copilot_narrative(user_id="rohan", investment_amount=5000.0)
        self.assertIn("headline", res)
        self.assertIn("voice_script", res)
        self.assertIn("Rohan", res["voice_script"])

    def test_manual_transaction_addition(self):
        expense = ManualExpenseInput(
            description="Weekend Staycation",
            amount=8500.0,
            category=ExpenseCategory.DISCRETIONARY,
            is_recurring=False
        )
        res = add_manual_transaction(expense=expense, user_id="rohan")
        self.assertEqual(res["status"], "success")
        self.assertIn("new_disposable_income", res)

    def test_account_aggregator_sandbox_flow(self):
        req = AAConsentRequest(
            mobile_number="9876543210",
            selected_fip_banks=["HDFC", "SBI"],
            data_range_months=6
        )
        init_res = initiate_aa_flow(req)
        self.assertIn("consent_id", init_res)
        self.assertEqual(init_res["status"], "OTP_SENT")

        verify_res = verify_aa_otp(consent_id=init_res["consent_id"], otp="4521")
        self.assertEqual(verify_res.status, "ACTIVE_CONSENT_GRANTED")
        self.assertGreater(verify_res.fip_count, 0)

    # ---------------------------------------------
    # Chatbot & Multilingual Tests
    # ---------------------------------------------
    def test_chatbot_emi_query_english(self):
        req = ChatRequest(query="Can I buy a 40,000 phone on 6-month EMI?", user_id="rohan", lang="en")
        res = chat_with_copilot(req)
        self.assertIn("40,000", res.reply)
        self.assertEqual(res.status_tag, "RISKY_PURCHASE")
        self.assertGreater(len(res.suggested_followups), 0)

    def test_chatbot_marathi_localization(self):
        req = ChatRequest(query="मी ₹40,000 चा फोन 6 महिन्यांच्या EMI वर घेऊ शकतो का?", user_id="rohan", lang="mr")
        res = chat_with_copilot(req)
        self.assertIn("सावधान", res.reply)
        self.assertIn("हप्ता", res.reply)

    def test_chatbot_hindi_localization(self):
        req = ChatRequest(query="क्या मैं ₹30,000 का फोन ईएमआई पर ले सकता हूँ?", user_id="priya", lang="hi")
        res = chat_with_copilot(req)
        self.assertIn("ईएमआई", res.reply)
        self.assertEqual(res.status_tag, "SAFE_PURCHASE")

    def test_chatbot_expense_reduction(self):
        req = ChatRequest(query="What if I cut dining out by 30%?", user_id="rohan", lang="en")
        res = chat_with_copilot(req)
        self.assertEqual(res.status_tag, "OPTIMIZATION_OPPORTUNITY")
        self.assertIn("30%", res.reply)

    def test_translations_endpoint(self):
        for lang in ["en", "hi", "mr"]:
            data = get_translations(lang)
            self.assertEqual(data["lang"], lang)
            self.assertIn("app_title", data["strings"])
            self.assertIn("code", data["speech_config"])


if __name__ == "__main__":
    unittest.main()
