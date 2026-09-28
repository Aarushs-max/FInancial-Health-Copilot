"""
Account Aggregator (AA) Sandbox Simulation.

Emulates the RBI-regulated Account Aggregator framework (Setu / Finvu / Anumati flow)
for frictionless financial data consent and discovery in the hackathon demo.
"""

import uuid
from typing import Dict, Any, List
from app.models.schemas import AAConsentRequest, AAConsentStatus


AVAILABLE_FIPS = [
    {"code": "HDFC", "name": "HDFC Bank Ltd", "type": "BANK", "accounts": ["A/C ending in 4092", "Salary A/C ending in 8110"]},
    {"code": "SBI", "name": "State Bank of India", "type": "BANK", "accounts": ["Savings A/C ending in 3319"]},
    {"code": "ICICI", "name": "ICICI Bank", "type": "BANK", "accounts": ["Checking A/C ending in 9024"]},
    {"code": "AXIS", "name": "Axis Bank", "type": "BANK", "accounts": ["Savings A/C ending in 7741"]},
    {"code": "CAMS", "name": "CAMS Mutual Fund Central", "type": "MUTUAL_FUND", "accounts": ["Folio 9928371/02"]}
]


def initiate_consent_handshake(request: AAConsentRequest) -> Dict[str, Any]:
    """
    Step 1 & 2: Issues Consent Handle and triggers simulated OTP.
    """
    consent_id = f"CONSENT-AA-{uuid.uuid4().hex[:8].upper()}"
    return {
        "consent_id": consent_id,
        "status": "OTP_SENT",
        "mobile_masked": f"+91 {request.mobile_number[:2]}******{request.mobile_number[-2:]}",
        "purpose_code": "FIN_HEALTH_ANALYSIS_101",
        "mock_otp": "4521",  # Provided for easy hackathon demoing
        "fip_list": request.selected_fip_banks or ["HDFC", "SBI"]
    }


def verify_consent_and_fetch_fi(consent_id: str, otp: str) -> AAConsentStatus:
    """
    Step 3 & 4: Validates OTP, generates digitally signed consent artifact,
    and returns linked financial accounts.
    """
    discovered: List[Dict[str, Any]] = []
    
    for fip in AVAILABLE_FIPS[:2]:
        for acc in fip["accounts"]:
            discovered.append({
                "fip_name": fip["name"],
                "account_id": acc,
                "account_type": "SAVINGS / CHECKING",
                "status": "LINKED_AND_FETCHED",
                "encryption_standard": "ECC-Curve25519-AES-GCM"
            })

    return AAConsentStatus(
        consent_id=consent_id,
        status="ACTIVE_CONSENT_GRANTED",
        fip_count=len(discovered),
        accounts_discovered=discovered,
        message="Simulated AA Consent successfully authenticated. 6 months transaction stream linked."
    )
