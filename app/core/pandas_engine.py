"""
Pandas-Powered Financial Processing Core.
Matches Slide 4 ("Deterministic affordability math engine (Pandas)")
and Slide 6 ("Growth Projections & Validated Impact").

Performs vectorized transaction aggregations, 5-year compounding trajectories (Y0-Y5),
and 7-day rolling daily liquidity balance modeling.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from app.models.schemas import UserProfile, ExpenseCategory


def build_transactions_dataframe(profile: UserProfile) -> pd.DataFrame:
    """Converts a UserProfile transactions list into a pandas DataFrame."""
    if not profile.transactions:
        return pd.DataFrame(columns=[
            "id", "date", "description", "amount", "category",
            "is_recurring", "due_day_of_month", "account_source"
        ])

    data = [
        {
            "id": tx.id,
            "date": tx.date,
            "description": tx.description,
            "amount": abs(float(tx.amount)),
            "category": tx.category.value,
            "is_recurring": bool(tx.is_recurring),
            "due_day_of_month": tx.due_day_of_month,
            "account_source": tx.account_source
        }
        for tx in profile.transactions
    ]
    df = pd.DataFrame(data)
    return df


def calculate_pandas_breakdown(profile: UserProfile) -> Dict[str, float]:
    """
    Computes vectorized financial totals using Pandas:
      - fixed_commitments (Rent, EMIs, Insurance)
      - lifestyle_spend (Dining, Shopping, Leisure)
      - utility_spend
      - total_monthly_burn
      - disposable_surplus
    """
    df = build_transactions_dataframe(profile)
    if df.empty:
        return {
            "fixed_commitments": 0.0,
            "lifestyle_spend": 0.0,
            "utility_spend": 0.0,
            "total_monthly_burn": 0.0,
            "disposable_surplus": float(profile.monthly_income)
        }

    # Group by category using Pandas
    cat_series = df.groupby("category")["amount"].sum()

    fixed = float(cat_series.get(ExpenseCategory.FIXED_OBLIGATION.value, 0.0))
    utility = float(cat_series.get(ExpenseCategory.UTILITY.value, 0.0))
    essential = float(cat_series.get(ExpenseCategory.ESSENTIAL_LIVING.value, 0.0))
    lifestyle = float(cat_series.get(ExpenseCategory.DISCRETIONARY.value, 0.0))

    fixed_total = fixed + utility + essential
    total_burn = fixed_total + lifestyle
    disposable = max(0.0, float(profile.monthly_income) - total_burn)

    return {
        "fixed_commitments": round(fixed_total, 2),
        "lifestyle_spend": round(lifestyle, 2),
        "utility_spend": round(utility, 2),
        "total_monthly_burn": round(total_burn, 2),
        "disposable_surplus": round(disposable, 2)
    }


def compute_5year_projections_dataset(monthly_investment: float) -> Dict[str, Any]:
    """
    Computes exact 5-Year Horizon growth projection matching Slide 6:
      - Horizon: Y0, Y1, Y2, Y3, Y4, Y5
      - 3 Series:
        1. Equity SIP Historical (~12% CAGR)
        2. Conservative Return (~6.5% CAGR)
        3. No-Growth Cash Baseline (0% CAGR)
    """
    years = [0, 1, 2, 3, 4, 5]
    labels = ["Y0", "Y1", "Y2", "Y3", "Y4", "Y5"]

    sip_series = []
    cons_series = []
    cash_series = []

    r_sip = (12.0 / 100.0) / 12.0
    r_cons = (6.5 / 100.0) / 12.0

    for yr in years:
        if yr == 0:
            sip_series.append(0.0)
            cons_series.append(0.0)
            cash_series.append(0.0)
        else:
            n = yr * 12
            invested = round(monthly_investment * n, 2)
            # SIP compounding formula: P * (((1+r)^n - 1) / r) * (1+r)
            fv_sip = monthly_investment * (((1.0 + r_sip) ** n - 1.0) / r_sip) * (1.0 + r_sip)
            fv_cons = monthly_investment * (((1.0 + r_cons) ** n - 1.0) / r_cons) * (1.0 + r_cons)

            sip_series.append(round(fv_sip, 0))
            cons_series.append(round(fv_cons, 0))
            cash_series.append(invested)

    return {
        "labels": labels,
        "sip_series": sip_series,
        "conservative_series": cons_series,
        "cash_series": cash_series,
        "monthly_amount": monthly_investment,
        "horizon_years": 5
    }


def compute_7day_liquidity_trajectory(profile: UserProfile, reference_day: int = 28) -> Dict[str, Any]:
    """
    Projects daily checking account balance over a 7-day rolling window (Day 0 to Day 7).
    Models each day's opening balance, debits hitting on that day, and closing balance.
    Flags the red shortfall danger dip if balance drops below ₹0.
    """
    df = build_transactions_dataframe(profile)
    start_balance = float(profile.liquid_savings)

    # Days in window: Day 0 (today) to Day 7
    days = list(range(8))
    labels = [f"Day {d}" for d in days]
    balance_curve = []
    debit_events = []

    current_balance = start_balance
    balance_curve.append(round(current_balance, 0))

    recurring_df = df[(df["is_recurring"] == True) & (df["due_day_of_month"].notna())] if not df.empty else pd.DataFrame()

    has_deficit = False
    min_balance = start_balance

    for d in range(1, 8):
        cal_day = (reference_day + d - 1) % 30 + 1  # 30-day month wrap
        day_debits = 0.0

        if not recurring_df.empty:
            day_matches = recurring_df[recurring_df["due_day_of_month"] == cal_day]
            if not day_matches.empty:
                for _, row in day_matches.iterrows():
                    amt = float(row["amount"])
                    day_debits += amt
                    debit_events.append({
                        "day_index": d,
                        "day_label": f"Day {d}",
                        "description": row["description"],
                        "amount": amt
                    })

        current_balance -= day_debits
        if current_balance < 0:
            has_deficit = True
        min_balance = min(min_balance, current_balance)
        balance_curve.append(round(current_balance, 0))

    shortfall = max(0.0, -min_balance)

    return {
        "day_labels": labels,
        "balance_series": balance_curve,
        "starting_balance": start_balance,
        "ending_balance": current_balance,
        "min_balance": min_balance,
        "shortfall_amount": shortfall,
        "has_deficit": has_deficit,
        "debit_events": debit_events
    }
