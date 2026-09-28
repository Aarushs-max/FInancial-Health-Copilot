# HackMatrix 5.0 (FIN-02) Judge Pitch & Demo Walkthrough Guide
> **Event:** HackMatrix 5.0 (Track: FIN-02 — PCCOE Pune)  
> **Target Demo Duration:** 3 to 4 Minutes  
> **Key Winning Differentiators:** FinCopilot Chatbot + Regional Marathi/Hindi Accessibility + Deterministic Affordability Math

---

## 🎤 3-Minute Winning Pitch Script for Judges

### 1. The Hook (30 Seconds)
> *"Judges, let me ask a simple question: What happens when an app tells someone earning ₹1.25 Lakhs in Pune or Bengaluru to 'just invest 20%'?  
> Most robo-advisors assume high income equals high investment capacity. But if that person pays ₹55,000 in rent and EMIs, and ₹50,000 in living expenses, they have **only ₹10,000 in true disposable margin**. A generic 20% rule (₹25,000) will literally bounce their cheques!  
> Welcome to **Financial Health Copilot** — an SDG-aligned decision-support copilot built with **true disposable affordability**, proactive **7-day cash-flow warnings**, an interactive **FinCopilot Chatbot**, and full **regional language accessibility in English, हिन्दी, and मराठी**."*

---

### 2. Live Demo Sequence (2.5 Minutes)

#### Step 1: Demonstrate Regional Accessibility (PCCOE Pune Special!)
1. Open [http://127.0.0.1:8000](http://127.0.0.1:8000).
2. Point to the top bar and click **मराठी (Marathi)**:
   - Show how the entire dashboard, KPIs (*खर्च करण्यायोग्य निव्वळ शिल्लक*, *नियमित देणी*), and risk badges seamlessly adapt into Marathi.
   - Click the **Speaker** icon: The Copilot speaks aloud in native Marathi (`mr-IN`)!
   - Highlight **SDG 10 (Reduced Inequalities)**: Financial guidance should not be restricted to English-fluent metro users.

#### Step 2: Test the Interactive FinCopilot Chatbot
1. In the **FinCopilot Assistant** panel, click the quick prompt chip:
   👉 *"Can I buy a ₹40,000 phone on 6-mo EMI?"* (Or in Marathi: *"मी ₹40,000 चा फोन 6 महिन्यांच्या EMI वर घेऊ का?"*)
2. Watch the Chatbot evaluate Rohan's verified cash flow in real time:
   - *"Caution! A ₹40,000 purchase on a 6-month tenure requires ₹6,667/month. This leaves only ₹3,333 in disposable buffer. Flagged as RISKY."*
3. Now test an optimization scenario:
   👉 *"What if I cut dining out by 30%?"*
   - Chatbot immediately calculates that cutting 30% saves ₹8,400/month and boosts disposable income to ₹18,400.

#### Step 3: Demonstrate Rohan (High Earner Trap) vs Priya (Frugal Saver)
1. Show **Rohan Mehta**:
   - Monthly Income: **₹1,25,000** | Disposable Surplus: **₹10,000** | Emergency Buffer: **0.4 months**
   - Drag the slider to **₹15,000**: turns **ROSE (Critical / Unaffordable)**. Copilot recommends a safe ceiling of ₹4,000.
2. Click **Priya (Frugal)**:
   - Monthly Income: **₹52,000** | Disposable Surplus: **₹24,000** (2.4x higher than Rohan!) | Emergency Buffer: **5.8 months**
   - Move slider to **₹10,000**: turns **EMERALD (Safe & Affordable)**.

#### Step 4: Amit Verma (Proactive 7-Day Cash-Flow Guard)
1. Click **Amit (Crunch)**:
2. Instantly, the top banner flashes **High-Priority Red Alert**:
   - *"Impending Liquidity Deficit: Shortfall of ₹11,000!"*
   - Identifies the exact driving auto-debits: Flat Rent (₹16,000) and SBI Education Loan (₹9,500) due in 3 days vs ₹14,500 bank balance.
   - Proactive remediation advice before bank defaults occur.

#### Step 5: Simulated Account Aggregator (AA) Sandbox
1. Click **Link Account (AA Sandbox)**.
2. Enter mobile number, view FIP banks (HDFC, SBI), enter sandbox OTP `4521`.
3. Demonstrates compliance with the RBI Account Aggregator protocol without third-party screen-scraping.

---

### 3. The Close (30 Seconds)
> *"To summarize: We didn't build another generic expense tracker. We built a regional, accessible, and mathematically sound copilot that protects users from debt spirals, explains every prediction, and speaks their language. Thank you!"*
