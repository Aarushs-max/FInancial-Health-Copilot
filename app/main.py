"""
Financial Health Copilot - Main Application Server.
HackMatrix 5.0 (FIN-02: SDG-Driven AI/ML Hackathon, PCCOE Pune)
Presented by Team Doom's Army: Aarush Shukla, Shubham Prajapat, Om Pandey, Om Kumbhar.

FastAPI server exposing:
  - Multi-Chart Graphical Analytics (5-Year Horizon Y0-Y5, Donut Breakdown, 7-Day Liquidity Area Chart)
  - Pandas-Powered Processing Core
  - Calibrated Disposable Affordability Math (Buffer = Income - Mandatory Obligations - Emergency Fund)
  - Forward 7-Day Cash-Flow Guard
  - FinCopilot Context-Aware Chatbot
  - Multilingual Localization (English, हिन्दी, मराठी)
  - Simulated Account Aggregator (AA) Sandbox (Setu/Finvu mock flow)
"""

import os
import uuid
import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    UserProfile, AffordabilityResult, CashFlowForecast,
    ImpactProjectionResult, ExplainabilityItem, ManualExpenseInput,
    AAConsentRequest, AAConsentStatus, Transaction, ExpenseCategory,
    ChatRequest, ChatResponse
)
from app.data.personas import PERSONAS
from app.core.affordability import evaluate_affordability
from app.core.cashflow_guard import analyze_7day_cashflow
from app.core.projections import generate_impact_projections
from app.core.explainability import generate_explainability_audit
from app.core.aa_sandbox import initiate_consent_handshake, verify_consent_and_fetch_fi
from app.core.copilot_narrator import synthesize_copilot_narrative
from app.core.copilot_chat import handle_copilot_chat
from app.core.localization import get_translations_for_lang, get_speech_config
from app.core.pandas_engine import (
    calculate_pandas_breakdown,
    compute_5year_projections_dataset,
    compute_7day_liquidity_trajectory
)

app = FastAPI(
    title="Financial Health Copilot API (Doom's Army — HackMatrix 5.0)",
    description="SDG-aligned personalized financial health copilot powered by Pandas, calibrated disposable affordability, proactive 7-day cash flow warnings, and multilingual chatbot.",
    version="2.0.0"
)

# Enable CORS for local testing & demos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active session state storage (in-memory per-session for the prototype)
active_profiles: Dict[str, UserProfile] = {k: v.model_copy(deep=True) for k, v in PERSONAS.items()}
current_active_user_id = "rohan"
live_sync_counter = 42


@app.get("/api/health")
def health_check():
    """Liveness probe."""
    return {
        "status": "ok",
        "app": "Financial Health Copilot",
        "team": "Doom's Army",
        "version": "2.0.0",
        "hackathon": "HackMatrix 5.0 (PCCOE Pune)"
    }


@app.get("/api/translations/{lang}")
def get_translations(lang: str = "en"):
    """Returns UI translation key-value dictionary for requested language."""
    return {
        "lang": lang,
        "strings": get_translations_for_lang(lang),
        "speech_config": get_speech_config(lang)
    }


@app.get("/api/personas")
def get_personas():
    """Returns metadata for all judge demo personas."""
    return [
        {
            "id": p.id,
            "name": p.name,
            "occupation": p.occupation,
            "city": p.city,
            "monthly_income": p.monthly_income,
            "liquid_savings": p.liquid_savings,
            "summary_tag": (
                "High Earner, High Burn Trap" if p.id == "rohan"
                else "Prudent Moderate Saver" if p.id == "priya"
                else "Imminent 5-Day Cash Crunch"
            )
        }
        for p in active_profiles.values()
    ]


@app.get("/api/profile/{user_id}")
def get_profile(user_id: str):
    """Fetches full state of a user profile."""
    if user_id not in active_profiles:
        raise HTTPException(status_code=404, detail="User profile not found")
    return active_profiles[user_id]


@app.post("/api/personas/select/{user_id}")
def select_active_persona(user_id: str):
    """Sets the active demo persona."""
    global current_active_user_id
    if user_id not in active_profiles:
        raise HTTPException(status_code=404, detail="User persona not found")
    current_active_user_id = user_id
    return {"active_user_id": current_active_user_id, "name": active_profiles[user_id].name}


@app.post("/api/personas/reset")
def reset_personas():
    """Resets persona data back to initial seeds."""
    global active_profiles
    active_profiles = {k: v.model_copy(deep=True) for k, v in PERSONAS.items()}
    return {"status": "reset_successful"}


# ==========================================
# Comprehensive Multi-Chart Graphical Analytics
# ==========================================
@app.get("/api/analytics/dashboard")
def get_graphical_dashboard_data(
    user_id: Optional[str] = None,
    investment_amount: float = Query(default=5000.0, ge=0.0),
    reference_day: int = Query(default=28, ge=1, le=31)
):
    """
    Returns unified multi-graph analytics payload powered by Pandas:
      1. 5-Year Horizon Projections (Slide 6): Y0 to Y5 comparing SIP (12%), Conservative (6.5%), Cash (0%)
      2. Capital Allocation Donut Breakdown: Fixed vs Lifestyle vs Emergency Fund vs Disposable Buffer
      3. 7-Day Rolling Daily Liquidity Trajectory Area Chart: projected balance curve with danger deficit dip
      4. Affordability Health Score & Status
      5. 3 Impact Benefit Cards (Zero Default Risk, Smart Wealth Building, Financial Inclusion)
    """
    uid = user_id or current_active_user_id
    if uid not in active_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = active_profiles[uid]

    # 1. Pandas Vectorized Breakdown
    pandas_metrics = calculate_pandas_breakdown(profile)
    affordability = evaluate_affordability(profile, investment_amount)
    cashflow = analyze_7day_cashflow(profile, reference_day=reference_day)

    # 2. 5-Year Compounding Horizon (Slide 6 Chart)
    projections_5yr = compute_5year_projections_dataset(investment_amount)

    # 3. 7-Day Daily Liquidity Balance Curve (Area Chart)
    liquidity_7day = compute_7day_liquidity_trajectory(profile, reference_day=reference_day)

    # 4. Capital Allocation Donut Data
    allocation_donut = {
        "labels": ["Fixed Obligations (Rent/EMIs)", "Discretionary Lifestyle", "Retained Emergency Cushion", "Disposable Surplus"],
        "values": [
            pandas_metrics["fixed_commitments"],
            pandas_metrics["lifestyle_spend"],
            round(min(profile.liquid_savings, pandas_metrics["fixed_commitments"] * 3), 2),
            pandas_metrics["disposable_surplus"]
        ],
        "colors": ["#f43f5e", "#f59e0b", "#6366f1", "#0ea5e9"]
    }

    # 5. Affordability Health Score (0-100)
    # Score incorporates emergency runway and buffer drain
    runway_score = min(50.0, affordability.emergency_fund_months * 10.0) # max 50 for 5+ months
    drain_factor = max(0.0, 50.0 - (affordability.buffer_drain_pct * 0.5)) # max 50 for low drain
    health_score = round(runway_score + drain_factor, 1)

    # 6. Slide 6 Validated Impact Cards
    impact_cards = {
        "zero_default_risk": {
            "title": "Zero Default Risk",
            "stat": "100%",
            "desc": "Protection against short-term bill defaults via 7-day predictive cash-flow warnings.",
            "status": "DANGER" if cashflow.has_cashflow_warning else "PROTECTED"
        },
        "smart_wealth_building": {
            "title": "Smart Wealth Building",
            "stat": f"{affordability.emergency_fund_months} Months",
            "desc": f"Calibrated recommendations always preserve a 3–6 month emergency cushion (Holding ₹{profile.liquid_savings:,.0f}).",
            "status": "ADEQUATE" if affordability.emergency_fund_months >= 3.0 else "VULNERABLE"
        },
        "financial_inclusion": {
            "title": "Financial Inclusion",
            "stat": "3 Languages",
            "desc": "Multilingual voice & chat onboarding (English, हिन्दी, मराठी) removes digital and literacy barriers.",
            "status": "ACTIVE"
        }
    }

    return {
        "user_id": uid,
        "user_name": profile.name,
        "tested_investment": investment_amount,
        "pandas_metrics": pandas_metrics,
        "affordability": affordability,
        "cashflow": cashflow,
        "projections_5yr": projections_5yr,
        "liquidity_7day": liquidity_7day,
        "allocation_donut": allocation_donut,
        "health_score": health_score,
        "impact_cards": impact_cards,
        "sync_timestamp": datetime.datetime.now().isoformat()
    }


# ==========================================
# Slide 7 Research & References Endpoint
# ==========================================
@app.get("/api/compliance/references")
def get_research_and_references():
    """Returns official research and regulatory frameworks from Slide 7."""
    return {
        "regulatory_guardrails": [
            {
                "title": "RBI Master Direction (NBFC-AA 2016)",
                "category": "Regulatory Framework",
                "summary": "Non-Banking Financial Company - Account Aggregator (Reserve Bank) Directions, 2016 governing explicit consent-based financial data sharing."
            },
            {
                "title": "Digital Personal Data Protection Act, 2023 (DPDP)",
                "category": "Data Privacy",
                "summary": "Government of India (MeitY) compliance for user consent revocation, purpose limitation, and zero data leakage."
            },
            {
                "title": "SEBI (Investment Advisers) Regulations, 2013",
                "category": "Advisory Guardrails",
                "summary": "Strict non-advisory educational boundaries ensuring output is classified as decision-support guidance, not fee-based registered advice."
            },
            {
                "title": "RBI Guidelines on Floating-Rate EMI Loans",
                "category": "Banking Policy",
                "summary": "Benchmarks for loan foreclosure, reset periodicity, and prepayment penalty guardrails."
            },
            {
                "title": "UN Sustainable Development Goals (SDG 8 & SDG 10)",
                "category": "Social Impact",
                "summary": "Promoting sustained economic growth, financial literacy, and reduced inequality across regional languages."
            },
            {
                "title": "Sahamati Account Aggregator Collective",
                "category": "Industry Body",
                "summary": "Standardized interoperable APIs, technical schemas, and certified consent manager specifications."
            }
        ],
        "technical_stack_references": [
            "Deterministic, auditable affordability & disposable-income formulas (rule-based, not LLM-generated)",
            "Python FastAPI + Pandas calculation engine for vectorized financial analysis",
            "Hosted LLM API with tool-calling for contextual natural-language explanations",
            "Speech-to-Text multilingual models — English, हिन्दी, मराठी",
            "Firebase Firestore & Realtime Database sync simulation"
        ]
    }


# ==========================================
# Core Financial Calculation Endpoints
# ==========================================
@app.get("/api/affordability", response_model=AffordabilityResult)
def check_affordability(
    user_id: Optional[str] = None,
    investment_amount: float = Query(default=5000.0, ge=0.0)
):
    """Evaluates personalized affordability for a proposed monthly investment amount."""
    uid = user_id or current_active_user_id
    if uid not in active_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = active_profiles[uid]
    return evaluate_affordability(profile, investment_amount)


@app.get("/api/cashflow-guard", response_model=CashFlowForecast)
def check_cashflow_guard(
    user_id: Optional[str] = None,
    reference_day: int = Query(default=28, ge=1, le=31)
):
    """Checks upcoming 5-7 days of recurring bills vs liquid balance."""
    uid = user_id or current_active_user_id
    if uid not in active_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = active_profiles[uid]
    return analyze_7day_cashflow(profile, reference_day=reference_day)


@app.get("/api/projections", response_model=ImpactProjectionResult)
def get_projections(investment_amount: float = Query(default=5000.0, ge=0.0)):
    """Computes compound impact projections (SIP 12%, Conservative 6.5%, Cash 0%)."""
    return generate_impact_projections(investment_amount)


@app.get("/api/explainability", response_model=List[ExplainabilityItem])
def get_explainability(
    user_id: Optional[str] = None,
    investment_amount: float = Query(default=5000.0, ge=0.0)
):
    """Generates transparent explainability provenance cards (Fact vs Prediction vs Reco)."""
    uid = user_id or current_active_user_id
    if uid not in active_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = active_profiles[uid]
    affordability = evaluate_affordability(profile, investment_amount)
    cashflow = analyze_7day_cashflow(profile)
    return generate_explainability_audit(profile, affordability, cashflow)


@app.get("/api/copilot/narrate")
def get_copilot_narrative(
    user_id: Optional[str] = None,
    investment_amount: float = Query(default=5000.0, ge=0.0)
):
    """Generates conversational narrative and Web Speech API speech script."""
    uid = user_id or current_active_user_id
    if uid not in active_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = active_profiles[uid]
    affordability = evaluate_affordability(profile, investment_amount)
    cashflow = analyze_7day_cashflow(profile)
    return synthesize_copilot_narrative(profile, affordability, cashflow)


# ==========================================
# Interactive Copilot Chatbot Endpoint
# ==========================================
@app.post("/api/chat", response_model=ChatResponse)
def chat_with_copilot(req: ChatRequest):
    """
    Evaluates free-form user financial questions in English, Hindi, or Marathi
    against deterministic equations and returns contextual financial counsel.
    """
    uid = req.user_id or current_active_user_id
    if uid not in active_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = active_profiles[uid]
    result = handle_copilot_chat(profile, req.query, lang=req.lang)
    return ChatResponse(
        reply=result["reply"],
        voice_script=result["voice_script"],
        status_tag=result["status_tag"],
        suggested_followups=result.get("suggested_followups", [])
    )


@app.post("/api/transactions/add")
def add_manual_transaction(
    expense: ManualExpenseInput,
    user_id: Optional[str] = None
):
    """
    Adds a manual expense or recurring bill to the active profile.
    Triggers immediate recalibration of all downstream health metrics and live sync stream.
    """
    global live_sync_counter
    uid = user_id or current_active_user_id
    if uid not in active_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = active_profiles[uid]
    new_tx = Transaction(
        id=f"tx-man-{uuid.uuid4().hex[:6]}",
        date="2026-09-27",
        description=expense.description,
        amount=expense.amount,
        category=expense.category,
        is_recurring=expense.is_recurring,
        due_day_of_month=expense.due_day_of_month,
        account_source="Manual User Entry"
    )
    profile.transactions.append(new_tx)
    live_sync_counter += 1

    affordability = evaluate_affordability(profile, 5000.0)
    cashflow = analyze_7day_cashflow(profile)

    return {
        "status": "success",
        "sync_event_id": f"RTDB-EVT-{live_sync_counter}",
        "added_transaction": new_tx,
        "new_disposable_income": affordability.disposable_income,
        "cashflow_warning": cashflow.has_cashflow_warning,
        "total_transactions": len(profile.transactions)
    }


# ==========================================
# Simulated Account Aggregator (AA) Endpoints
# ==========================================
@app.post("/api/aa/initiate")
def initiate_aa_flow(req: AAConsentRequest):
    """Initiates Setu/Finvu style AA consent request and sends simulated OTP."""
    return initiate_consent_handshake(req)


@app.post("/api/aa/verify-otp")
def verify_aa_otp(consent_id: str = Query(...), otp: str = Query(...)):
    """Verifies OTP and attaches newly fetched bank account transactions."""
    status = verify_consent_and_fetch_fi(consent_id, otp)
    return status


# Mount static directory for frontend UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def serve_index():
    """Serves the main Financial Health Copilot web dashboard."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Financial Health Copilot API is running. Visit /docs for Swagger UI."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
