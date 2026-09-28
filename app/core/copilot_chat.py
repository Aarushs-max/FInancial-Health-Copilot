"""
Conversational Financial Copilot Chatbot Engine.
Provides natural language reasoning over a user's financial reality:
  - Affordability of major purchases (e.g., iPhone on EMI, vacation)
  - What-if expense reduction scenarios (e.g., cutting dining out)
  - 7-day cash flow diagnostics and shortfall explanations
  - Emergency fund gap analysis
Supports localized output in English, Hindi, and Marathi.
"""

import re
from typing import Dict, Any, List
from app.models.schemas import UserProfile, ExpenseCategory
from app.core.affordability import evaluate_affordability, calculate_expense_breakdown
from app.core.cashflow_guard import analyze_7day_cashflow


def handle_copilot_chat(
    profile: UserProfile,
    query: str,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Evaluates natural user questions against deterministic financial equations
    and returns a localized, context-aware answer with actionable advice.
    """
    q_lower = query.lower().strip()
    fixed_spend, lifestyle_spend, total_spend = calculate_expense_breakdown(profile)
    disposable = max(0.0, profile.monthly_income - total_spend)
    cashflow = analyze_7day_cashflow(profile)
    emergency_months = round(profile.liquid_savings / max(1000.0, fixed_spend), 1)

    # -------------------------------------------------------------
    # Scenario 1: EMI & Major Purchase Affordability
    # e.g., "Can I buy a 40,000 phone on 6-month EMI?"
    # -------------------------------------------------------------
    if any(k in q_lower for k in ["emi", "phone", "iphone", "laptop", "buy", "purchase", "afford to buy", "हप्ता", "फोन", "घेऊ शकतो"]):
        # Extract purchase amount if mentioned
        amounts = [int(s) for s in re.findall(r'\b\d+(?:,\d+)?\b', q_lower.replace(",", ""))]
        total_price = amounts[0] if amounts else 36000
        tenure = 6
        for t in [3, 6, 9, 12, 18, 24]:
            if f"{t} month" in q_lower or f"{t}-month" in q_lower or f"{t} महिने" in q_lower:
                tenure = t
                break

        monthly_emi = round(total_price / tenure, 0)
        remaining_buffer_after_emi = disposable - monthly_emi
        is_affordable = remaining_buffer_after_emi >= 4000 and disposable > monthly_emi

        if is_affordable:
            if lang == "mr":
                reply = (
                    f"होय, तुम्ही ₹{total_price:,.0f} चा खरेदी हप्ता परवडू शकता. "
                    f"{tenure} महिन्यांसाठी अंदाजे हप्ता ₹{monthly_emi:,.0f}/महिना असेल. "
                    f"तुमच्याकडे सध्या ₹{disposable:,.0f} शिल्लक आहे, हप्ता भरल्यानंतरही "
                    f"तुमच्याकडे ₹{remaining_buffer_after_emi:,.0f} सुरक्षित बफर राहील."
                )
                voice_text = f"होय, तुम्ही हा हप्ता सहज भरू शकता. मासिक हप्ता रुपये {int(monthly_emi):,} असेल."
            elif lang == "hi":
                reply = (
                    f"हाँ, आप ₹{total_price:,.0f} की खरीदारी का ईएमआई उठा सकते हैं। "
                    f"{tenure} महीनों के लिए मासिक ईएमआई लगभग ₹{monthly_emi:,.0f} होगी। "
                    f"आपके पास ₹{disposable:,.0f} की मासिक बचत है, अतः ईएमआई के बाद भी "
                    f"₹{remaining_buffer_after_emi:,.0f} का सुरक्षित बफर बचेगा।"
                )
                voice_text = f"हाँ, आप यह ईएमआई ले सकते हैं। मासिक ईएमआई रुपये {int(monthly_emi):,} होगी।"
            else:
                reply = (
                    f"Yes, this purchase is affordable! A ₹{total_price:,.0f} purchase over {tenure} months "
                    f"results in an estimated EMI of ₹{monthly_emi:,.0f}/month. "
                    f"With your ₹{disposable:,.0f} disposable surplus, you comfortably retain a ₹{remaining_buffer_after_emi:,.0f} "
                    f"monthly safety buffer."
                )
                voice_text = f"Yes, you can afford this. The monthly EMI would be {int(monthly_emi)} rupees, leaving a healthy buffer."

            status_tag = "SAFE_PURCHASE"
        else:
            if lang == "mr":
                reply = (
                    f"सावधान! ₹{total_price:,.0f} ची खरेदी सध्या धोकादायक ठरू शकते. "
                    f"मासिक हप्ता ₹{monthly_emi:,.0f} असेल, ज्यामुळे तुमची शिल्लक फक्त ₹{max(0.0, remaining_buffer_after_emi):,.0f} राहील. "
                    f"आधी आपत्कालीन निधी ३ महिने सुरक्षित करा किंवा खरेदी काही महिने पुढे ढकला."
                )
                voice_text = f"सावधान! हा हप्ता तुमच्या मासिक बजेटवर ताण आणेल. खरेदी पुढे ढकलण्याचा विचार करा."
            elif lang == "hi":
                reply = (
                    f"सावधान! ₹{total_price:,.0f} की खरीदारी फिलहाल जोखिम भरी है। "
                    f"मासिक ईएमआई ₹{monthly_emi:,.0f} होगी, जिससे आपका बफर घटकर केवल ₹{max(0.0, remaining_buffer_after_emi):,.0f} रह जाएगा। "
                    f"हम सलाह देते हैं कि पहले आपातकालीन फंड को मजबूत करें।"
                )
                voice_text = f"सावधान! यह ईएमआई आपके मासिक बफर को समाप्त कर देगी। इसे अभी टालना बेहतर होगा।"
            else:
                reply = (
                    f"Caution! A ₹{total_price:,.0f} purchase on a {tenure}-month tenure requires ₹{monthly_emi:,.0f}/month. "
                    f"This leaves only ₹{max(0.0, remaining_buffer_after_emi):,.0f} in disposable buffer. "
                    f"Any emergency expense would force you into high-interest revolving credit."
                )
                voice_text = f"Caution. An EMI of {int(monthly_emi)} rupees cuts too deep into your remaining buffer."

            status_tag = "RISKY_PURCHASE"

        return {
            "reply": reply,
            "voice_script": voice_text,
            "status_tag": status_tag,
            "suggested_followups": [
                "What if I choose a 12-month tenure?",
                "How much emergency fund do I need?",
                "What is my safe monthly ceiling?"
            ]
        }

    # -------------------------------------------------------------
    # Scenario 2: What-if Expense Reduction
    # e.g., "What if I cut dining out by 30%?"
    # -------------------------------------------------------------
    if any(k in q_lower for k in ["cut", "reduce", "dining", "swiggy", "lifestyle", "कमी", "हॉटेलिंग", "घटा"]):
        savings_boost = round(lifestyle_spend * 0.30, -2)
        new_disposable = disposable + savings_boost
        if lang == "mr":
            reply = (
                f"छान कल्पना! जर तुम्ही जीवनशैली आणि हॉटेलिंग खर्च ३०% ने कमी केला, "
                f"तर तुम्ही दरमहा अतिरिक्त ₹{savings_boost:,.0f} वाचवू शकाल. "
                f"यामुळे तुमची मासिक शिल्लक ₹{disposable:,.0f} वरून वाढून ₹{new_disposable:,.0f} होईल, "
                f"ज्यामुळे तुमची गुंतवणूक क्षमता लगेच वाढेल!"
            )
            voice_text = f"उत्तम विचार! हॉटेलिंग ३० टक्के कमी केल्यास दरमहा रुपये {int(savings_boost):,} अतिरिक्त वाचतील."
        elif lang == "hi":
            reply = (
                f"शानदार विचार! यदि आप अपने जीवनशैली और बाहर खाने के खर्च में 30% की कटौती करते हैं, "
                f"तो आप हर महीने अतिरिक्त ₹{savings_boost:,.0f} की बचत करेंगे। "
                f"आपकी कुल बचत क्षमता ₹{disposable:,.0f} से बढ़कर ₹{new_disposable:,.0f} हो जाएगी!"
            )
            voice_text = f"अच्छा विचार है! जीवनशैली खर्च कम करने से आप हर महीने रुपये {int(savings_boost):,} अतिरिक्त बचा सकते हैं।"
        else:
            reply = (
                f"Great strategy! Trimming your lifestyle expenses by 30% frees up an extra ₹{savings_boost:,.0f}/month. "
                f"This boosts your true disposable surplus from ₹{disposable:,.0f} to ₹{new_disposable:,.0f}, "
                f"enabling you to safely increase your SIP investments."
            )
            voice_text = f"Cutting discretionary spend by 30 percent saves you an extra {int(savings_boost)} rupees every month."

        return {
            "reply": reply,
            "voice_script": voice_text,
            "status_tag": "OPTIMIZATION_OPPORTUNITY",
            "suggested_followups": [
                f"Can I afford to invest ₹{int(new_disposable * 0.5):,} now?",
                "How much will this grow in 5 years?",
                "Analyze my upcoming 7-day bills"
            ]
        }

    # -------------------------------------------------------------
    # Scenario 3: Cash Flow Shortfall / Upcoming Bills Diagnostic
    # e.g., "Why is my 7-day cash flow at risk?"
    # -------------------------------------------------------------
    if any(k in q_lower for k in ["shortfall", "risk", "cash flow", "danger", "bill", "rent", "तूट", "संकट", "खतरा", "कमी"]):
        if cashflow.has_cashflow_warning:
            drivers = ", ".join([f"{u.description} (₹{u.amount:,.0f})" for u in cashflow.driving_obligations[:2]])
            if lang == "mr":
                reply = (
                    f"तुमच्या बँक खात्यात पुढील ७ दिवसांत ₹{cashflow.projected_shortfall:,.0f} ची तूट होण्याची शक्यता आहे. "
                    f"कारण: एकूण देणी ₹{cashflow.total_upcoming_bills:,.0f} आहेत, पण खात्यात फक्त ₹{cashflow.liquid_available_balance:,.0f} उपलब्ध आहेत. "
                    f"प्रमुख कारण: {drivers}. "
                    f"हप्ते बाऊन्स होण्यापासून वाचवण्यासाठी त्वरित निधी हस्तांतरित करा."
                )
                voice_text = f"सावधान! पुढील सात दिवसांत रुपये {int(cashflow.projected_shortfall):,} ची तूट दिसत आहे. खात्यात पैसे जमा करा."
            elif lang == "hi":
                reply = (
                    f"आपके बैंक खाते में अगले 7 दिनों में ₹{cashflow.projected_shortfall:,.0f} की कमी हो सकती है। "
                    f"कारण: कुल देय बिल ₹{cashflow.total_upcoming_bills:,.0f} हैं जबकि बैंक में केवल ₹{cashflow.liquid_available_balance:,.0f} हैं। "
                    f"मुख्य बिल: {drivers}। ईएमआई बाउंस से बचने के लिए तुरंत खाते में राशि ट्रांसफर करें।"
                )
                voice_text = f"ध्यान दें! अगले 7 दिनों में रुपये {int(cashflow.projected_shortfall):,} की कमी हो सकती है। तुरंत व्यवस्था करें।"
            else:
                reply = (
                    f"Warning: A projected liquidity shortfall of ₹{cashflow.projected_shortfall:,.0f} will occur within 7 days. "
                    f"Upcoming auto-debits total ₹{cashflow.total_upcoming_bills:,.0f}, while your liquid checking balance is ₹{cashflow.liquid_available_balance:,.0f}. "
                    f"Drivers: {drivers}. Transfer funds immediately to avoid bounce charges."
                )
                voice_text = f"Warning! You have a projected shortfall of {int(cashflow.projected_shortfall)} rupees within the next 7 days."
            status_tag = "CASHFLOW_ALERT"
        else:
            if lang == "mr":
                reply = (
                    f"तुमचा पुढील ७ दिवसांचा रोख प्रवाह पूर्णपणे सुरक्षित आहे! "
                    f"येणारे बिल ₹{cashflow.total_upcoming_bills:,.0f} आहे, तर तुमच्या खात्यात ₹{cashflow.liquid_available_balance:,.0f} शिल्लक आहे. "
                    f"सर्व खर्च भागवून ₹{cashflow.projected_closing_balance:,.0f} शिल्लक राहील."
                )
                voice_text = "पुढील सात दिवसांसाठी रोख प्रवाह सुरक्षित आहे. काळजीचे कारण नाही."
            elif lang == "hi":
                reply = (
                    f"आपका आगामी 7 दिनों का नकदी प्रवाह पूरी तरह सुरक्षित है। "
                    f"आगामी बिल ₹{cashflow.total_upcoming_bills:,.0f} हैं और खाते में ₹{cashflow.liquid_available_balance:,.0f} मौजूद हैं। "
                    f"बिल कटने के बाद भी ₹{cashflow.projected_closing_balance:,.0f} शेष रहेंगे।"
                )
                voice_text = "आगामी 7 दिनों के लिए आपका कैश फ्लो बिल्कुल स्थिर है।"
            else:
                reply = (
                    f"Your upcoming 7-day cash flow is stable! Scheduled obligations of ₹{cashflow.total_upcoming_bills:,.0f} "
                    f"are fully covered by your ₹{cashflow.liquid_available_balance:,.0f} liquid balance, leaving a healthy ₹{cashflow.projected_closing_balance:,.0f} surplus."
                )
                voice_text = "Your 7-day cash flow is well funded and safe."
            status_tag = "CASHFLOW_STABLE"

        return {
            "reply": reply,
            "voice_script": voice_text,
            "status_tag": status_tag,
            "suggested_followups": [
                "How much should I keep in checking account?",
                "Can I afford to invest this month?",
                "What is my emergency fund status?"
            ]
        }

    # -------------------------------------------------------------
    # Scenario 4: Specific SIP / Investment Amount Query
    # e.g., "Can I afford ₹8,000 SIP?"
    # -------------------------------------------------------------
    nums = [int(s) for s in re.findall(r'\b\d+(?:,\d+)?\b', q_lower.replace(",", ""))]
    if nums or "invest" in q_lower or "sip" in q_lower or "गुंतवणूक" in q_lower or "निवेश" in q_lower:
        amt = nums[0] if nums else 5000
        afford = evaluate_affordability(profile, amt)

        if lang == "mr":
            reply = (
                f"मासिक ₹{amt:,.0f} च्या गुंतवणुकीचे विश्लेषण: **{afford.risk_badge_text}**\n\n"
                f"{afford.detailed_rationale}\n"
                f"• खर्च करण्यायोग्य शिल्लक: ₹{afford.disposable_income:,.0f}\n"
                f"• गुंतवणूक केल्यानंतर उरणारा बफर: ₹{afford.remaining_disposable_buffer:,.0f}\n"
                f"• आपत्कालीन निधी कव्हर: {afford.emergency_fund_months} महिने"
            )
            voice_text = f"रुपये {amt} गुंतवणुकीबाबत: {afford.headline_verdict}"
        elif lang == "hi":
            reply = (
                f"मासिक ₹{amt:,.0f} निवेश का विश्लेषण: **{afford.risk_badge_text}**\n\n"
                f"{afford.detailed_rationale}\n"
                f"• बचत योग्य शुद्ध आय: ₹{afford.disposable_income:,.0f}\n"
                f"• निवेश उपरांत शेष बफर: ₹{afford.remaining_disposable_buffer:,.0f}\n"
                f"• आपातकालीन फंड सुरक्षा: {afford.emergency_fund_months} महीने"
            )
            voice_text = f"रुपये {amt} के निवेश पर निष्कर्ष: {afford.headline_verdict}"
        else:
            reply = (
                f"Affordability Verdict for ₹{amt:,.0f}/month: **{afford.risk_badge_text}**\n\n"
                f"{afford.detailed_rationale}\n"
                f"• True Disposable Income: ₹{afford.disposable_income:,.0f}\n"
                f"• Post-Investment Buffer: ₹{afford.remaining_disposable_buffer:,.0f}\n"
                f"• Emergency Runway: {afford.emergency_fund_months} months"
            )
            voice_text = f"For {amt} rupees monthly: {afford.headline_verdict}"

        return {
            "reply": reply,
            "voice_script": voice_text,
            "status_tag": afford.risk_status.value,
            "suggested_followups": [
                f"Show expected returns for ₹{amt:,} in 5 years",
                "What is my safe recommended ceiling?",
                "Can I buy a phone on EMI?"
            ]
        }

    # -------------------------------------------------------------
    # Default: Comprehensive Financial Health Summary
    # -------------------------------------------------------------
    if lang == "mr":
        reply = (
            f"नमस्कार {profile.name.split()[0]}! तुमचा सध्याचा आर्थिक अहवाल:\n"
            f"• मासिक उत्पन्न: ₹{profile.monthly_income:,.0f}\n"
            f"• नियमित खर्च व देणी: ₹{fixed_spend:,.0f}\n"
            f"• जीवनशैली खर्च: ₹{lifestyle_spend:,.0f}\n"
            f"• खरी खर्च करण्यायोग्य शिल्लक: ₹{disposable:,.0f}/महिना\n"
            f"• आपत्कालीन निधी: {emergency_months} महिन्यांचा खर्च (₹{profile.liquid_savings:,.0f})\n\n"
            f"तुम्ही कोणत्याही खरेदीबद्दल (उदा. फोन ईएमआई, एसआयपी किंवा बिले) प्रश्न विचारू शकता."
        )
        voice_text = f"नमस्कार {profile.name.split()[0]}. तुमची मासिक शिल्लक रुपये {int(disposable):,} आहे."
    elif lang == "hi":
        reply = (
            f"नमस्ते {profile.name.split()[0]}! आपकी वित्तीय स्वास्थ्य स्थिति:\n"
            f"• कुल मासिक आय: ₹{profile.monthly_income:,.0f}\n"
            f"• निश्चित देनदारियां: ₹{fixed_spend:,.0f}\n"
            f"• जीवनशैली खर्च: ₹{lifestyle_spend:,.0f}\n"
            f"• शुद्ध बचत योग्य आय: ₹{disposable:,.0f}/माह\n"
            f"• आपातकालीन सुरक्षा: {emergency_months} महीने (₹{profile.liquid_savings:,.0f})\n\n"
            f"आप किसी भी खरीदारी, ईएमआई या निवेश पर तुरंत सलाह ले सकते हैं।"
        )
        voice_text = f"नमस्ते {profile.name.split()[0]}. आपकी शुद्ध बचत क्षमता रुपये {int(disposable):,} है।"
    else:
        reply = (
            f"Hello {profile.name.split()[0]}! Here is your personalized financial health summary:\n"
            f"• Monthly Inflow: ₹{profile.monthly_income:,.0f}\n"
            f"• Fixed Commitments (Debt/Rent): ₹{fixed_spend:,.0f}\n"
            f"• Discretionary Lifestyle Burn: ₹{lifestyle_spend:,.0f}\n"
            f"• True Disposable Margin: ₹{disposable:,.0f}/month\n"
            f"• Emergency Runway: {emergency_months} months (₹{profile.liquid_savings:,.0f} liquid)\n\n"
            f"Ask me about any scenario, major purchase, or EMI to see if it is safe for you."
        )
        voice_text = f"Hello {profile.name.split()[0]}. Your monthly disposable margin is {int(disposable)} rupees."

    return {
        "reply": reply,
        "voice_script": voice_text,
        "status_tag": "PROFILE_SUMMARY",
        "suggested_followups": [
            "Can I afford ₹8,000 SIP?",
            "Can I buy a ₹40,000 phone on EMI?",
            "Why is my 7-day cash flow at risk?"
        ]
    }
