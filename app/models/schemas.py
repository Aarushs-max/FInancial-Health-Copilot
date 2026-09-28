"""
Pydantic data schemas representing financial entities, assessment metrics,
projections, explainability tags, and interactive chatbot models.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ExpenseCategory(str, Enum):
    FIXED_OBLIGATION = "fixed_obligation"  # Rent, EMI, Insurance, Child Education
    UTILITY = "utility"                    # Electricity, Broadband, Maintenance
    DISCRETIONARY = "discretionary"        # Dining out, entertainment, gadgets, travel
    ESSENTIAL_LIVING = "essential_living"  # Groceries, fuel, medical essentials


class RiskTier(str, Enum):
    SAFE = "SAFE"
    MODERATE = "MODERATE"
    RISKY = "RISKY"
    CRITICAL = "CRITICAL"


class InsightType(str, Enum):
    OBSERVED_FACT = "OBSERVED_FACT"
    MODEL_PREDICTION = "MODEL_PREDICTION"
    ACTIONABLE_RECOMMENDATION = "ACTIONABLE_RECOMMENDATION"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Transaction(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    category: ExpenseCategory
    is_recurring: bool = False
    due_day_of_month: Optional[int] = None
    account_source: str = "HDFC Bank (Primary)"


class UserProfile(BaseModel):
    id: str
    name: str
    occupation: str
    city: str
    monthly_income: float
    liquid_savings: float
    emergency_fund_target_months: int = 6
    risk_tolerance: str = "moderate"
    transactions: List[Transaction] = Field(default_factory=list)


class AffordabilityResult(BaseModel):
    monthly_income: float
    fixed_obligations: float
    lifestyle_expenses: float
    total_monthly_spend: float
    disposable_income: float
    disposable_income_ratio: float
    liquid_savings: float
    emergency_fund_months: float
    tested_investment_amount: float
    remaining_disposable_buffer: float
    buffer_drain_pct: float
    risk_status: RiskTier
    risk_badge_text: str
    headline_verdict: str
    detailed_rationale: str
    safe_recommended_investment_ceiling: float


class UpcomingObligation(BaseModel):
    description: str
    amount: float
    due_date_formatted: str
    days_until_due: int
    category: str


class CashFlowForecast(BaseModel):
    has_cashflow_warning: bool
    evaluation_window_days: int = 7
    liquid_available_balance: float
    total_upcoming_bills: float
    projected_shortfall: float
    projected_closing_balance: float
    driving_obligations: List[UpcomingObligation]
    warning_title: str
    warning_message: str
    recommended_action: str


class ProjectionPoint(BaseModel):
    year: int
    total_invested: float
    conservative_value: float  # e.g., 6.5% Debt / Fixed Return
    balanced_sip_value: float  # e.g., 12.0% Historical Equity SIP
    cash_baseline_value: float # 0.0% Cash baseline


class ImpactProjectionResult(BaseModel):
    monthly_investment: float
    scenarios: List[ProjectionPoint]
    assumed_sip_cagr_pct: float = 12.0
    assumed_conservative_cagr_pct: float = 6.5
    chart_labels: List[str]
    sip_series: List[float]
    conservative_series: List[float]
    cash_series: List[float]
    regulatory_disclaimer: str


class ExplainabilityItem(BaseModel):
    id: str
    type: InsightType
    title: str
    explanation: str
    confidence_level: ConfidenceLevel
    confidence_score: float  # 0.0 to 1.0
    data_provenance: str


class ManualExpenseInput(BaseModel):
    description: str
    amount: float
    category: ExpenseCategory
    is_recurring: bool = False
    due_day_of_month: Optional[int] = None


class AAConsentRequest(BaseModel):
    mobile_number: str
    selected_fip_banks: List[str]
    data_range_months: int = 6


class AAConsentStatus(BaseModel):
    consent_id: str
    status: str
    fip_count: int
    accounts_discovered: List[Dict[str, Any]]
    message: str


# Chatbot & Multilingual Models
class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    lang: str = "en"  # "en", "hi", "mr"


class ChatResponse(BaseModel):
    reply: str
    voice_script: str
    status_tag: str
    suggested_followups: List[str] = Field(default_factory=list)
