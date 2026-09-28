/**
 * Financial Health Copilot - Client State, Multilingual i18n & Chatbot.
 * Supports English, हिन्दी (hi), and मराठी (mr) with native Web Speech synthesis.
 */

let currentUserId = "rohan";
let currentLang = "en";
let currentTestedAmount = 5000;
let projectionChart = null;
let latestVoiceScript = "";
let isListening = false;
let recognition = null;
let currentTranslations = {};
let speechConfig = { code: "en-IN", rate: 1.0, pitch: 1.0 };

// Initialize on document load
document.addEventListener("DOMContentLoaded", async () => {
    lucide.createIcons();
    initProjectionChart();
    await switchLanguage("en");
    await loadPersonaState(currentUserId);
    initChatWelcome();
    setupSpeechRecognition();
});

// Switch language (en, hi, mr)
async function switchLanguage(lang) {
    currentLang = lang;
    ["en", "hi", "mr"].forEach(l => {
        const btn = document.getElementById(`lang-btn-${l}`);
        if (btn) {
            if (l === lang) {
                btn.className = "px-2.5 py-1 rounded font-bold bg-sky-600 text-white transition";
            } else {
                btn.className = "px-2.5 py-1 rounded font-medium text-slate-400 hover:text-white transition";
            }
        }
    });

    try {
        const res = await fetch(`/api/translations/${lang}`).then(r => r.json());
        currentTranslations = res.strings;
        speechConfig = res.speech_config;

        // Update all data-i18n elements
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (currentTranslations[key]) {
                el.innerText = currentTranslations[key];
            }
        });

        // Update placeholders
        document.querySelectorAll("[data-i18n-ph]").forEach(el => {
            const key = el.getAttribute("data-i18n-ph");
            if (currentTranslations[key]) {
                el.placeholder = currentTranslations[key];
            }
        });

        const langName = lang === "mr" ? "मराठी" : lang === "hi" ? "हिन्दी" : "English";
        const ind = document.getElementById("chat-lang-indicator");
        if (ind) ind.innerText = `Language: ${langName}`;

        const vTag = document.getElementById("voice-lang-tag");
        if (vTag) vTag.innerText = speechConfig.code;

        // Re-render chat welcome in the chosen language
        initChatWelcome();
        // Update speech recognition language
        if (recognition) {
            recognition.lang = speechConfig.code;
        }

        lucide.createIcons();
    } catch (err) {
        console.error("Language load error:", err);
    }
}

// Switch persona
async function switchPersona(userId) {
    currentUserId = userId;
    ["rohan", "priya", "amit"].forEach(u => {
        const btn = document.getElementById(`btn-persona-${u}`);
        if (btn) {
            if (u === userId) {
                btn.className = "px-2.5 py-1 rounded font-bold bg-sky-600 text-white shadow-sm transition";
            } else {
                btn.className = "px-2.5 py-1 rounded font-medium text-slate-400 hover:text-white transition";
            }
        }
    });

    await fetch(`/api/personas/select/${userId}`, { method: "POST" });
    await loadPersonaState(userId);
    initChatWelcome();
}

// Load full state for persona
async function loadPersonaState(userId) {
    try {
        const [profileRes, affordRes, cashflowRes, projRes, explainRes, narrateRes] = await Promise.all([
            fetch(`/api/profile/${userId}`).then(r => r.json()),
            fetch(`/api/affordability?user_id=${userId}&investment_amount=${currentTestedAmount}`).then(r => r.json()),
            fetch(`/api/cashflow-guard?user_id=${userId}`).then(r => r.json()),
            fetch(`/api/projections?investment_amount=${currentTestedAmount}`).then(r => r.json()),
            fetch(`/api/explainability?user_id=${userId}&investment_amount=${currentTestedAmount}`).then(r => r.json()),
            fetch(`/api/copilot/narrate?user_id=${userId}&investment_amount=${currentTestedAmount}`).then(r => r.json())
        ]);

        renderProfileHeader(profileRes);
        renderKPIs(profileRes, affordRes);
        renderAffordability(affordRes);
        renderCashFlowBanner(cashflowRes);
        renderProjections(projRes);
        renderExplainability(explainRes);
        renderTransactions(profileRes.transactions);

        latestVoiceScript = narrateRes.voice_script;
        lucide.createIcons();
    } catch (err) {
        console.error("Error loading copilot state:", err);
    }
}

// Render Profile Header
function renderProfileHeader(profile) {
    document.getElementById("profile-name").innerText = profile.name;
    document.getElementById("profile-occupation").innerText = profile.occupation;
    document.getElementById("profile-city").innerText = `• ${profile.city}`;
    document.getElementById("profile-initials").innerText = profile.name.split(" ").map(n => n[0]).join("");

    const tag = profile.id === "rohan" 
        ? "High Earner, High Burn Trap (Exposes flaws in generic 20% rules)"
        : profile.id === "priya"
        ? "Prudent Moderate Saver (High disposable surplus & 5.8 mos emergency cushion)"
        : "Imminent Cash-Flow Crunch (Bills due in 5 days exceed available bank balance)";
    document.getElementById("profile-summary-tag").innerText = tag;
}

// Render Top KPIs
function renderKPIs(profile, afford) {
    document.getElementById("kpi-income").innerText = `₹${afford.monthly_income.toLocaleString("en-IN")}`;
    document.getElementById("kpi-fixed").innerText = `₹${afford.fixed_obligations.toLocaleString("en-IN")}`;
    document.getElementById("kpi-lifestyle").innerText = `₹${afford.lifestyle_expenses.toLocaleString("en-IN")}`;
    document.getElementById("kpi-disposable").innerText = `₹${afford.disposable_income.toLocaleString("en-IN")}`;
    document.getElementById("kpi-emergency").innerText = `${afford.emergency_fund_months} ${currentTranslations["months"] || "Months"}`;
    document.getElementById("kpi-savings").innerText = `₹${afford.liquid_savings.toLocaleString("en-IN")} ${currentTranslations["liquid_savings"] || "liquid"}`;
}

// Render Affordability Box
function renderAffordability(afford) {
    document.getElementById("calc-disposable").innerText = `₹${afford.disposable_income.toLocaleString("en-IN")}`;
    document.getElementById("calc-buffer").innerText = `₹${afford.remaining_disposable_buffer.toLocaleString("en-IN")}`;
    document.getElementById("calc-drain").innerText = `${afford.buffer_drain_pct.toFixed(0)}%`;
    document.getElementById("calc-ceiling").innerText = `₹${afford.safe_recommended_investment_ceiling.toLocaleString("en-IN")}/mo`;

    const badge = document.getElementById("risk-badge");
    badge.innerText = afford.risk_badge_text;

    if (afford.risk_status === "SAFE") {
        badge.className = "px-3 py-1 rounded-full text-xs font-bold tracking-wide badge-reco";
    } else if (afford.risk_status === "MODERATE") {
        badge.className = "px-3 py-1 rounded-full text-xs font-bold tracking-wide badge-pred";
    } else {
        badge.className = "px-3 py-1 rounded-full text-xs font-bold tracking-wide badge-danger";
    }

    document.getElementById("rationale-headline").innerHTML = `
        <i data-lucide="${afford.risk_status === 'SAFE' ? 'check-circle' : afford.risk_status === 'MODERATE' ? 'alert-circle' : 'alert-triangle'}" class="w-4 h-4 ${afford.risk_status === 'SAFE' ? 'text-emerald-400' : afford.risk_status === 'MODERATE' ? 'text-amber-400' : 'text-rose-400'}"></i>
        <span>${afford.headline_verdict}</span>
    `;
    document.getElementById("rationale-detail").innerText = afford.detailed_rationale;
}

// Render Cash Flow Warning Banner
function renderCashFlowBanner(cf) {
    const container = document.getElementById("cashflow-banner-container");
    if (!cf.has_cashflow_warning) {
        container.innerHTML = `
            <div class="glass-card p-3.5 bg-emerald-950/20 border-emerald-500/30 flex items-center justify-between text-xs text-emerald-300">
                <div class="flex items-center gap-2">
                    <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-400"></i>
                    <span><strong>7-Day Cash-Flow Guard:</strong> Scheduled debits of ₹${cf.total_upcoming_bills.toLocaleString("en-IN")} are fully cushioned by ₹${cf.liquid_available_balance.toLocaleString("en-IN")} balance.</span>
                </div>
                <span class="text-[11px] text-emerald-400/80">No Shortfall Predicted</span>
            </div>
        `;
    } else {
        const drivers = cf.driving_obligations.map(d => `<span class="bg-rose-900/40 px-1.5 py-0.5 rounded text-rose-200 border border-rose-500/30">${d.description} (₹${d.amount.toLocaleString("en-IN")})</span>`).join(" ");
        container.innerHTML = `
            <div class="glass-card p-4 bg-rose-950/40 border-rose-500/50 space-y-2">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2 text-rose-300 font-bold text-sm">
                        <i data-lucide="alert-octagon" class="w-5 h-5 text-rose-400"></i>
                        <span>${cf.warning_title}</span>
                    </div>
                    <span class="text-xs font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">Action Required</span>
                </div>
                <p class="text-xs text-slate-300">${cf.warning_message}</p>
                <div class="flex items-center gap-2 text-xs text-slate-400">
                    <span class="font-semibold text-slate-300">Impending Drivers:</span>
                    <div>${drivers}</div>
                </div>
                <div class="p-2.5 rounded bg-slate-900/90 text-xs text-amber-300 border border-amber-500/30">
                    <strong>Recommended Action:</strong> ${cf.recommended_action}
                </div>
            </div>
        `;
    }
}

// Render Chart.js Projection
function initProjectionChart() {
    const ctx = document.getElementById("projectionChart").getContext("2d");
    projectionChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: ["Year 1", "Year 3", "Year 5", "Year 10"],
            datasets: [
                {
                    label: "Equity SIP (12% CAGR)",
                    data: [0, 0, 0, 0],
                    borderColor: "#38bdf8",
                    backgroundColor: "rgba(56, 189, 248, 0.1)",
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.3
                },
                {
                    label: "Conservative FD (6.5% CAGR)",
                    data: [0, 0, 0, 0],
                    borderColor: "#818cf8",
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    borderDash: [4, 4],
                    tension: 0.3
                },
                {
                    label: "Cash Mattress (0% Baseline)",
                    data: [0, 0, 0, 0],
                    borderColor: "#64748b",
                    backgroundColor: "transparent",
                    borderWidth: 1.5,
                    borderDash: [2, 2],
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                    labels: { color: "#94a3b8", font: { size: 10 } }
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.dataset.label}: ₹${Math.round(ctx.parsed.y).toLocaleString("en-IN")}`
                    }
                }
            },
            scales: {
                x: { ticks: { color: "#64748b", font: { size: 10 } }, grid: { color: "rgba(255,255,255,0.05)" } },
                y: {
                    ticks: {
                        color: "#64748b",
                        font: { size: 10 },
                        callback: (v) => v >= 100000 ? `₹${(v/100000).toFixed(1)}L` : `₹${(v/1000).toFixed(0)}k`
                    },
                    grid: { color: "rgba(255,255,255,0.05)" }
                }
            }
        }
    });
}

function renderProjections(proj) {
    if (!projectionChart) return;
    projectionChart.data.labels = proj.chart_labels;
    projectionChart.data.datasets[0].data = proj.sip_series;
    projectionChart.data.datasets[1].data = proj.conservative_series;
    projectionChart.data.datasets[2].data = proj.cash_series;
    projectionChart.update();
}

// Render Explainability Cards
function renderExplainability(items) {
    const feed = document.getElementById("explainability-feed");
    feed.innerHTML = items.map(item => {
        const badgeClass = item.type === "OBSERVED_FACT" ? "badge-fact"
            : item.type === "MODEL_PREDICTION" ? "badge-pred"
            : "badge-reco";
        const icon = item.type === "OBSERVED_FACT" ? "database"
            : item.type === "MODEL_PREDICTION" ? "trending-up"
            : "zap";

        return `
            <div class="glass-card p-4 flex flex-col justify-between space-y-2">
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <span class="${badgeClass} px-2 py-0.5 rounded text-[10px] font-mono font-bold">
                            ${item.type.replace("_", " ")}
                        </span>
                        <span class="text-[10px] text-slate-400 font-mono">
                            ${(item.confidence_score * 100).toFixed(0)}% Conf.
                        </span>
                    </div>
                    <h5 class="text-xs font-bold text-white flex items-center gap-1.5">
                        <i data-lucide="${icon}" class="w-3.5 h-3.5 text-slate-400"></i>
                        <span>${item.title}</span>
                    </h5>
                    <p class="text-xs text-slate-400 mt-1 leading-relaxed">${item.explanation}</p>
                </div>
                <div class="pt-2 border-t border-slate-800 text-[10px] text-slate-500 font-mono">
                    Src: ${item.data_provenance}
                </div>
            </div>
        `;
    }).join("");
    lucide.createIcons();
}

// Render Transaction Table
function renderTransactions(txs) {
    document.getElementById("tx-count-badge").innerText = `${txs.length} transactions active`;
    const tbody = document.getElementById("transaction-rows");
    tbody.innerHTML = txs.map(tx => {
        const isRec = tx.is_recurring ? `<span class="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px] font-medium">Monthly Auto-Debit</span>` : `<span class="text-slate-500 text-[10px]">One-Time</span>`;
        const dueText = tx.due_day_of_month ? `Day ${tx.due_day_of_month}` : tx.date;
        const catClean = tx.category.replace("_", " ").toUpperCase();
        return `
            <tr class="hover:bg-slate-900/40 transition">
                <td class="py-2.5 px-3 font-semibold text-white">${tx.description}</td>
                <td class="py-2.5 px-3 text-[11px] text-slate-400">${catClean}</td>
                <td class="py-2.5 px-3">${isRec}</td>
                <td class="py-2.5 px-3 text-slate-400 font-mono text-[11px]">${dueText}</td>
                <td class="py-2.5 px-3 text-right font-mono font-bold text-slate-200">₹${tx.amount.toLocaleString("en-IN")}</td>
            </tr>
        `;
    }).join("");
}

// Amount slider & input handler
let debounceTimer = null;
function onAmountChanged(val) {
    const num = Math.max(500, Math.min(50000, Number(val) || 500));
    currentTestedAmount = num;
    document.getElementById("investment-slider").value = num;
    document.getElementById("investment-input").value = num;

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
        const [affordRes, projRes, narrateRes] = await Promise.all([
            fetch(`/api/affordability?user_id=${currentUserId}&investment_amount=${currentTestedAmount}`).then(r => r.json()),
            fetch(`/api/projections?investment_amount=${currentTestedAmount}`).then(r => r.json()),
            fetch(`/api/copilot/narrate?user_id=${currentUserId}&investment_amount=${currentTestedAmount}`).then(r => r.json())
        ]);
        renderAffordability(affordRes);
        renderProjections(projRes);
        latestVoiceScript = narrateRes.voice_script;
        lucide.createIcons();
    }, 150);
}

// ==========================================
// FinCopilot Interactive Chatbot
// ==========================================
function initChatWelcome() {
    const chatContainer = document.getElementById("chat-messages");
    if (!chatContainer) return;

    let welcomeText = "";
    if (currentLang === "mr") {
        welcomeText = `नमस्कार! मी तुमचा <strong>फिन-कोपायलट</strong> सहाय्यक आहे. मी तुमच्या उत्पन्नाचा, नियमित कर्जाचा आणि पुढील ७ दिवसांच्या बिलांचा अभ्यास केला आहे. तुम्हाला कोणतीही खरेदी परवडेल का किंवा एसआयपी कशी सुरू करावी याबद्दल विचारा!`;
    } else if (currentLang === "hi") {
        welcomeText = `नमस्ते! मैं आपका <strong>फिन-कोपायलट</strong> सहायक हूँ। मैंने आपके आय-व्यय और आगामी 7 दिनों के बिलां का विश्लेषण किया है। आप मुझसे किसी भी ईएमआई, खरीदारी या एसआईपी पर सीधे सलाह ले सकते हैं।`;
    } else {
        welcomeText = `Hello! I am your <strong>FinCopilot</strong> assistant. I have evaluated your verified cash flow, recurring obligations, and emergency runway. Ask me any question like <em>"Can I buy an iPhone on EMI?"</em> or test any scenario!`;
    }

    chatContainer.innerHTML = `
        <div class="flex items-start gap-2.5">
            <div class="h-7 w-7 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                <i data-lucide="bot" class="w-3.5 h-3.5"></i>
            </div>
            <div class="chat-bubble-bot">
                ${welcomeText}
            </div>
        </div>
    `;
    lucide.createIcons();
}

async function handleChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("chat-input");
    const query = input.value.trim();
    if (!query) return;

    input.value = "";
    await sendChatMessage(query);
}

async function triggerQuickPrompt(text) {
    await sendChatMessage(text);
}

async function sendChatMessage(query) {
    const chatContainer = document.getElementById("chat-messages");

    // 1. Append user bubble
    const userDiv = document.createElement("div");
    userDiv.className = "flex justify-end";
    userDiv.innerHTML = `<div class="chat-bubble-user">${escapeHtml(query)}</div>`;
    chatContainer.appendChild(userDiv);

    // 2. Append typing indicator
    const typingId = `typing-${Date.now()}`;
    const typingDiv = document.createElement("div");
    typingDiv.id = typingId;
    typingDiv.className = "flex items-start gap-2.5";
    typingDiv.innerHTML = `
        <div class="h-7 w-7 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs shrink-0 mt-0.5">
            <i data-lucide="bot" class="w-3.5 h-3.5"></i>
        </div>
        <div class="chat-bubble-bot">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    lucide.createIcons();

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: query,
                user_id: currentUserId,
                lang: currentLang
            })
        }).then(r => r.json());

        // Remove typing indicator
        document.getElementById(typingId)?.remove();

        // Format response text with line breaks
        const formattedReply = res.reply.replace(/\n/g, "<br>");

        // Render Bot response
        const botDiv = document.createElement("div");
        botDiv.className = "flex items-start gap-2.5";
        botDiv.innerHTML = `
            <div class="h-7 w-7 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs shrink-0 mt-0.5">
                <i data-lucide="bot" class="w-3.5 h-3.5"></i>
            </div>
            <div class="chat-bubble-bot space-y-2">
                <div>${formattedReply}</div>
                <div class="flex items-center justify-between pt-1 border-t border-slate-700/50 text-[10px]">
                    <span class="text-sky-400 font-mono uppercase">${res.status_tag.replace("_", " ")}</span>
                    <button onclick="speakText('${escapeSpeech(res.voice_script)}')" class="text-slate-400 hover:text-white flex items-center gap-1">
                        <i data-lucide="volume-2" class="w-3 h-3"></i>
                        <span>Speak</span>
                    </button>
                </div>
            </div>
        `;
        chatContainer.appendChild(botDiv);

        // Update suggested prompt chips if provided
        if (res.suggested_followups && res.suggested_followups.length > 0) {
            const chipsContainer = document.getElementById("quick-prompt-chips");
            if (chipsContainer) {
                chipsContainer.innerHTML = res.suggested_followups.map(f => 
                    `<button onclick="triggerQuickPrompt('${escapeHtml(f)}')" class="prompt-chip">${escapeHtml(f)}</button>`
                ).join(" ");
            }
        }

        chatContainer.scrollTop = chatContainer.scrollHeight;
        lucide.createIcons();

        // Optionally play voice if audio was triggered by voice
        if (isListening) {
            speakText(res.voice_script);
        }
    } catch (err) {
        document.getElementById(typingId)?.remove();
        console.error("Chat error:", err);
    }
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
}

function escapeSpeech(text) {
    return text.replace(/'/g, "\\'").replace(/"/g, "&quot;");
}

// Web Speech API - Synthesis in current language
function speakText(text) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = speechConfig.code || "en-IN";
    utterance.rate = speechConfig.rate || 1.0;
    utterance.pitch = speechConfig.pitch || 1.0;
    window.speechSynthesis.speak(utterance);
}

function playVoiceSummary() {
    speakText(latestVoiceScript);
}

// Web Speech API - Speech Recognition (STT)
function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        const hint = document.getElementById("voice-status-text");
        if (hint) hint.innerText = "Voice input requires Chrome/Edge";
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = speechConfig.code || "en-IN";

    recognition.onstart = () => {
        isListening = true;
        document.getElementById("mic-btn").classList.add("listening-pulse", "bg-rose-500/30", "border-rose-500");
        document.getElementById("voice-status-text").innerText = "Listening... Ask any question!";
    };

    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("voice-status-text").innerText = `Heard: "${transcript}"`;
        // Send transcript directly to Copilot Chat
        await sendChatMessage(transcript);
    };

    recognition.onerror = () => {
        isListening = false;
        document.getElementById("mic-btn").classList.remove("listening-pulse", "bg-rose-500/30", "border-rose-500");
        document.getElementById("voice-status-text").innerText = currentTranslations["voice_hint"] || "Click mic or test: 'Can I afford 5,000?'";
    };

    recognition.onend = () => {
        isListening = false;
        document.getElementById("mic-btn").classList.remove("listening-pulse", "bg-rose-500/30", "border-rose-500");
    };
}

function toggleVoiceQuery() {
    if (!recognition) {
        playVoiceSummary();
        return;
    }
    if (isListening) {
        recognition.stop();
    } else {
        recognition.start();
    }
}

// Account Aggregator (AA) Simulation Modal Handlers
let activeConsentId = "";
function openAAModal() {
    document.getElementById("aa-modal").classList.remove("hidden");
    document.getElementById("aa-step-1").classList.remove("hidden");
    document.getElementById("aa-step-2").classList.add("hidden");
    document.getElementById("aa-step-3").classList.add("hidden");
    lucide.createIcons();
}

function closeAAModal() {
    document.getElementById("aa-modal").classList.add("hidden");
}

async function sendAAOTP() {
    const mobile = document.getElementById("aa-mobile").value || "9876543210";
    const res = await fetch("/api/aa/initiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile_number: mobile, selected_fip_banks: ["HDFC", "SBI"], data_range_months: 6 })
    }).then(r => r.json());

    activeConsentId = res.consent_id;
    document.getElementById("aa-consent-id").innerText = res.consent_id;
    document.getElementById("aa-step-1").classList.add("hidden");
    document.getElementById("aa-step-2").classList.remove("hidden");
    lucide.createIcons();
}

async function verifyAAOTP() {
    const otp = document.getElementById("aa-otp").value || "4521";
    await fetch(`/api/aa/verify-otp?consent_id=${activeConsentId}&otp=${otp}`, { method: "POST" });
    
    document.getElementById("aa-step-2").classList.add("hidden");
    document.getElementById("aa-step-3").classList.remove("hidden");
    document.getElementById("aa-status-badge").innerText = currentTranslations["aa_active"] || "AA Stream Active (Linked)";
    lucide.createIcons();
}

// Manual Expense Addition Handlers
function openTxModal() {
    document.getElementById("tx-modal").classList.remove("hidden");
    lucide.createIcons();
}

function closeTxModal() {
    document.getElementById("tx-modal").classList.add("hidden");
}

function toggleDueDayInput(isRecurring) {
    const wrapper = document.getElementById("due-day-wrapper");
    if (isRecurring) {
        wrapper.classList.remove("hidden");
    } else {
        wrapper.classList.add("hidden");
    }
}

async function submitManualExpense(e) {
    e.preventDefault();
    const desc = document.getElementById("manual-desc").value;
    const amt = parseFloat(document.getElementById("manual-amount").value);
    const cat = document.getElementById("manual-cat").value;
    const isRecurring = document.getElementById("manual-recurring").checked;
    const dueDayVal = document.getElementById("manual-dueday").value;
    const dueDay = (isRecurring && dueDayVal) ? parseInt(dueDayVal, 10) : null;

    await fetch(`/api/transactions/add?user_id=${currentUserId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            description: desc,
            amount: amt,
            category: cat,
            is_recurring: isRecurring,
            due_day_of_month: dueDay
        })
    });

    closeTxModal();
    document.getElementById("manual-desc").value = "";
    document.getElementById("manual-amount").value = "";
    document.getElementById("manual-recurring").checked = false;
    document.getElementById("due-day-wrapper").classList.add("hidden");

    await loadPersonaState(currentUserId);
}
