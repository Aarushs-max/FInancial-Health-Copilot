"""
Unit Test Suite for Financial Health Copilot Core Engines.
Verifies deterministic affordability calculations, cash-flow warning triggers,
and compound projection formulas.
"""

import unittest
from app.models.schemas import UserProfile, Transaction, ExpenseCategory, RiskTier
from app.core.affordability import evaluate_affordability
from app.core.cashflow_guard import analyze_7day_cashflow
from app.core.projections import calculate_sip_future_value, generate_impact_projections
from app.data.personas import PERSONAS


class TestAffordabilityEngine(unittest.TestCase):
    def test_rohan_high_burn_detects_risk(self):
        """Rohan earns 1.25L but spends 1.15L -> Disposable is 10k. Investing 15k must be CRITICAL."""
        rohan = PERSONAS["rohan"].model_copy(deep=True)
        result = evaluate_affordability(rohan, tested_amount=15000.0)
        self.assertEqual(result.risk_status, RiskTier.CRITICAL)
        self.assertTrue(result.remaining_disposable_buffer < 0)

    def test_priya_frugal_is_safe(self):
        """Priya earns 52k and spends 28k -> Disposable is 24k. Investing 5k must be SAFE."""
        priya = PERSONAS["priya"].model_copy(deep=True)
        result = evaluate_affordability(priya, tested_amount=5000.0)
        self.assertEqual(result.risk_status, RiskTier.SAFE)
        self.assertTrue(result.remaining_disposable_buffer > 15000)
        self.assertGreaterEqual(result.emergency_fund_months, 3.0)


class TestCashflowGuard(unittest.TestCase):
    def test_amit_detects_shortfall(self):
        """Amit has 14.5k liquid but bills due in next 5 days exceed 25k -> Must trigger warning."""
        amit = PERSONAS["amit"].model_copy(deep=True)
        forecast = analyze_7day_cashflow(amit, reference_day=28)
        self.assertTrue(forecast.has_cashflow_warning)
        self.assertGreater(forecast.projected_shortfall, 10000.0)
        self.assertGreater(len(forecast.driving_obligations), 0)


class TestImpactProjections(unittest.TestCase):
    def test_sip_compounding_math(self):
        """5,000/mo over 10 years at 12% CAGR should compound to over 11 Lakhs (vs 6L cash)."""
        fv = calculate_sip_future_value(5000.0, 12.0, 10)
        total_cash = 5000.0 * 12 * 10  # 600,000
        self.assertGreater(fv, 1100000.0)
        self.assertGreater(fv, total_cash)

    def test_projections_structure(self):
        res = generate_impact_projections(5000.0)
        self.assertEqual(len(res.scenarios), 4)
        self.assertEqual(len(res.chart_labels), 4)
        self.assertIn("SEBI", res.regulatory_disclaimer)


if __name__ == "__main__":
    unittest.main()
