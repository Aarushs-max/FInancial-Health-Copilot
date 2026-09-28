"""
Preloaded Judge Personas for HackMatrix 5.0 Demo.

Provides 3 distinct financial realities to demonstrate how generic percentage rules
fail while our calibrated disposable copilot delivers razor-sharp advice:
  1. Rohan Mehta: High income (₹1.25L), high burn (₹1.15L) -> Low buffer, risky to invest ₹15k.
  2. Priya Sharma: Moderate income (₹52k), frugal (₹28k spend) -> High buffer, safe to invest ₹12k.
  3. Amit Verma: Imminent 5-day cash crunch -> ₹25.5k bills due vs ₹14.5k balance.
"""

from typing import Dict
from app.models.schemas import UserProfile, Transaction, ExpenseCategory


PERSONAS: Dict[str, UserProfile] = {
    "rohan": UserProfile(
        id="rohan",
        name="Rohan Mehta",
        occupation="Senior Software Consultant",
        city="Bengaluru, KA",
        monthly_income=125000.0,
        liquid_savings=32000.0,  # Only ~0.4 months of essential burn!
        emergency_fund_target_months=6,
        risk_tolerance="moderate",
        transactions=[
            Transaction(id="tx-r1", date="2026-09-01", description="Apartment Rent (Indiranagar)", amount=35000.0, category=ExpenseCategory.FIXED_OBLIGATION, is_recurring=True, due_day_of_month=1),
            Transaction(id="tx-r2", date="2026-09-05", description="Sedan Car Loan EMI (HDFC)", amount=18000.0, category=ExpenseCategory.FIXED_OBLIGATION, is_recurring=True, due_day_of_month=5),
            Transaction(id="tx-r3", date="2026-09-10", description="Term & Health Insurance Premium", amount=4500.0, category=ExpenseCategory.FIXED_OBLIGATION, is_recurring=True, due_day_of_month=10),
            Transaction(id="tx-r4", date="2026-09-12", description="High-Speed Broadband & Utilities", amount=3500.0, category=ExpenseCategory.UTILITY, is_recurring=True, due_day_of_month=12),
            Transaction(id="tx-r5", date="2026-09-15", description="Credit Card Bill (Dining & Travel)", amount=28000.0, category=ExpenseCategory.DISCRETIONARY, is_recurring=True, due_day_of_month=15),
            Transaction(id="tx-r6", date="2026-09-18", description="Weekend Socializing & Microbreweries", amount=14000.0, category=ExpenseCategory.DISCRETIONARY, is_recurring=False),
            Transaction(id="tx-r7", date="2026-09-22", description="Online Gadgets & Subscriptions", amount=12000.0, category=ExpenseCategory.DISCRETIONARY, is_recurring=False),
        ]
    ),

    "priya": UserProfile(
        id="priya",
        name="Priya Sharma",
        occupation="UX Designer & Content Specialist",
        city="Pune, MH",
        monthly_income=52000.0,
        liquid_savings=145000.0,  # Robust ~5.8 months emergency cushion!
        emergency_fund_target_months=6,
        risk_tolerance="balanced",
        transactions=[
            Transaction(id="tx-p1", date="2026-09-01", description="Shared 2BHK Rent (Kothrud)", amount=12000.0, category=ExpenseCategory.FIXED_OBLIGATION, is_recurring=True, due_day_of_month=1),
            Transaction(id="tx-p2", date="2026-09-04", description="Electricity & Wi-Fi", amount=2200.0, category=ExpenseCategory.UTILITY, is_recurring=True, due_day_of_month=4),
            Transaction(id="tx-p3", date="2026-09-07", description="Groceries & Essentials (Blinkit)", amount=6800.0, category=ExpenseCategory.ESSENTIAL_LIVING, is_recurring=True, due_day_of_month=7),
            Transaction(id="tx-p4", date="2026-09-14", description="Weekend Cafe & Movies", amount=3500.0, category=ExpenseCategory.DISCRETIONARY, is_recurring=False),
            Transaction(id="tx-p5", date="2026-09-20", description="Bookstore & Digital Learning Subscriptions", amount=3500.0, category=ExpenseCategory.DISCRETIONARY, is_recurring=False),
        ]
    ),

    "amit": UserProfile(
        id="amit",
        name="Amit Verma",
        occupation="Operations Analyst",
        city="Hyderabad, TS",
        monthly_income=68000.0,  # Salary credited on 10th
        liquid_savings=14500.0,  # Imminent crunch!
        emergency_fund_target_months=6,
        risk_tolerance="conservative",
        transactions=[
            Transaction(id="tx-a1", date="2026-09-01", description="Flat Rent (Gachibowli)", amount=16000.0, category=ExpenseCategory.FIXED_OBLIGATION, is_recurring=True, due_day_of_month=1),
            Transaction(id="tx-a2", date="2026-09-03", description="Education Loan EMI (SBI)", amount=9500.0, category=ExpenseCategory.FIXED_OBLIGATION, is_recurring=True, due_day_of_month=3),
            Transaction(id="tx-a3", date="2026-09-06", description="Electricity & Water Board", amount=1800.0, category=ExpenseCategory.UTILITY, is_recurring=True, due_day_of_month=6),
            Transaction(id="tx-a4", date="2026-09-12", description="Discretionary Spend", amount=8000.0, category=ExpenseCategory.DISCRETIONARY, is_recurring=False),
        ]
    )
}
