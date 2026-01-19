// ==============================
// DOM ELEMENTS
// ==============================
const form = document.getElementById("recommendForm");
const modelViewer = document.getElementById("phone3D");
const resultsSummary = document.getElementById("results-summary");
const resultsList = document.getElementById("results-list");
const modeSelect = document.getElementById("modeSelect");

const printerOverlay = document.getElementById("printerOverlay");
const aiThinking = document.getElementById("aiThinking");
const thinkingSteps = Array.from(aiThinking.querySelectorAll(".thinking-step"));

// ==============================
// CONSTANTS — FAKE 3D PRINTER
// ==============================
const BASE_GLB   = "/static/recommender_app/models/base_phone.glb";
const DEVICE_GLB = "/static/recommender_app/models/device_phone.glb";
const DEFAULT_MESSAGE = "No results yet";

// ==============================
// EXPLAINABILITY BARS
// ==============================
function renderExplainabilityBars(scores) {
    if (!scores) return "";
    return `
        <div class="explain-bars">
            ${Object.entries(scores).map(([key, value]) => `
                <div class="bar-row">
                    <span class="bar-label">${key.replaceAll("_", " ")}</span>
                    <div class="bar-track">
                        <div class="bar-fill" style="width:${value}%"></div>
                    </div>
                    <span class="bar-value">${value}%</span>
                </div>
            `).join("")}
        </div>
    `;
}

// ==============================
// CSRF HELPER
// ==============================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        document.cookie.split(";").forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}
const csrftoken = getCookie("csrftoken");

// ==============================
// CLEAR RESULTS
// ==============================
function clearResults(message = DEFAULT_MESSAGE) {
    resultsSummary.textContent = message;
    resultsList.innerHTML = `<p class="placeholder">${message}</p>`;
}

// ==============================
// ANIMATE AI THINKING TIMELINE
// ==============================
async function runAIThinking() {
    aiThinking.classList.add("active");
    for (const step of thinkingSteps) {
        step.classList.add("active");
        await new Promise(resolve => setTimeout(resolve, 600));
    }
}

// ==============================
// RESET AI THINKING
// ==============================
function resetAIThinking() {
    aiThinking.classList.remove("active");
    thinkingSteps.forEach(step => step.classList.remove("active"));
}

// ==============================
// ANIMATE PRINTER OVERLAY
// ==============================
function animatePrinterOverlay(duration = 1500) {
    printerOverlay.style.width = "0%";
    printerOverlay.style.transition = `width ${duration}ms ease-in-out`;

    requestAnimationFrame(() => {
        printerOverlay.style.width = "100%";
    });

    return new Promise(resolve => setTimeout(resolve, duration));
}

// ==============================
// FAKE 3D PRINT TRIGGER
// ==============================
async function triggerFakePrint() {
    modelViewer.pause();
    modelViewer.removeAttribute("src");

    // Animate printing overlay
    await animatePrinterOverlay(1200);

    requestAnimationFrame(() => {
        modelViewer.src = DEVICE_GLB;
        modelViewer.play();
        printerOverlay.style.width = "0%";
    });
}

// ==============================
// CREATE RESULT CARD (NO IMAGES — EVER)
// ==============================
function createPhoneCard(item, index) {
    const specs = item.specs || {};
    const card = document.createElement("div");
    card.className = "result-card";

    card.innerHTML = `
        <div class="result-card-header">
            <div class="result-title">#${index + 1} • ${item.brand} ${item.model}</div>
            <div class="result-score">Match: ${Math.round(item.score * 100)}%</div>
        </div>

        <div class="result-body">
            <div class="result-specs">
                <div><strong>Price:</strong> $${specs.price ?? "N/A"}</div>
                <div><strong>Camera:</strong> ${specs.camera ?? "?"} MP</div>
                <div><strong>Battery:</strong> ${specs.battery ?? "?"} mAh</div>
                <div><strong>RAM:</strong> ${specs.ram ?? "?"} GB</div>
                <div><strong>Display:</strong> ${specs.display ?? "?"}</div>
                <div><strong>5G:</strong> ${specs.five_g ? "Yes" : "No"}</div>
                <div><strong>Year:</strong> ${specs.year ?? "?"}</div>
            </div>

            ${renderExplainabilityBars(item.feature_scores)}
        </div>

        <p class="result-why">
            ${(item.why && item.why.length)
                ? item.why.join(" • ")
                : "Strong overall match for your preferences"}
        </p>
    `;

    // Clicking a card re-triggers the 3D printer
    card.addEventListener("click", triggerFakePrint);

    return card;
}

// ==============================
// FORM SUBMISSION
// ==============================
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearResults("Analyzing your preferences…");
    resetAIThinking();
    await runAIThinking();

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    payload.mode = modeSelect ? modeSelect.value : "hybrid";

    try {
        const res = await fetch("/recommend/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const items = data.results || [];

        if (!items.length) {
            clearResults("No phones matched your criteria.");
            return;
        }

        resultsList.innerHTML = "";
        items.forEach((item, idx) => {
            resultsList.appendChild(createPhoneCard(item, idx));
        });

        // Trigger 3D printing after results appear
        await triggerFakePrint();

        resultsSummary.textContent = `Top ${items.length} matches • Mode: ${payload.mode}`;
    } catch (err) {
        console.error("Recommendation error:", err);
        clearResults("Something went wrong while retrieving recommendations.");
        resultsSummary.textContent = "Error";
    }
});

// ==============================
// INITIAL STATE
// ==============================
clearResults();
modelViewer.src = BASE_GLB;
