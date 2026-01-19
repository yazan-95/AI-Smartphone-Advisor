const form = document.getElementById("recommendForm");
const modelViewer = document.getElementById("phone3D");
const resultsSummary = document.getElementById("results-summary");
const resultsList = document.getElementById("results-list");

// -------------------------
// CSRF
// -------------------------
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

// -------------------------
// Poll 3D model (SAFE)
// -------------------------
function poll3DModel(statusUrl) {
    const interval = setInterval(() => {
        fetch(statusUrl)
            .then(res => res.json())
            .then(data => {
                if (data.status === "ready" && data.model_url) {
                    modelViewer.src = data.model_url;
                    resultsSummary.textContent = "3D model ready";
                    clearInterval(interval);
                }
            })
            .catch(err => {
                console.error("3D polling failed", err);
                clearInterval(interval);
            });
    }, 3000);
}

// -------------------------
// Form submit
// -------------------------
form.addEventListener("submit", function (e) {
    e.preventDefault();

    resultsSummary.textContent = "Analyzing your preferences…";
    resultsList.innerHTML = `<p class="placeholder">Running recommendation engine…</p>`;

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    fetch("/recommend/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
    })
    .then(data => {
        const items = data.results || [];
        if (!items.length) {
            resultsSummary.textContent = "No matches found";
            resultsList.innerHTML = `<p class="placeholder">No phones matched your criteria.</p>`;
            return;
        }

        resultsList.innerHTML = "";

        items.forEach((item, idx) => {
            const specs = item.specs || {};

            const card = document.createElement("div");
            card.className = "result-card";
            card.innerHTML = `
                <div class="result-card-header">
                    <div class="result-title">#${idx + 1} • ${item.model}</div>
                    <div class="result-score">Match: ${Math.round(item.score * 100)}%</div>
                </div>
                <div class="result-body">
                    <img src="/static/recommender_app/images/placeholder.png" class="result-image">
                    <div class="result-specs">
                        <div><strong>Price:</strong> $${specs.price ?? "N/A"}</div>
                        <div><strong>Camera:</strong> ${specs.camera ?? "?"} MP</div>
                        <div><strong>Battery:</strong> ${specs.battery ?? "?"} mAh</div>
                        <div><strong>RAM:</strong> ${specs.ram ?? "?"} GB</div>
                        <div><strong>Display:</strong> ${specs.display ?? "?"}</div>
                        <div><strong>5G:</strong> ${specs.five_g ? "Yes" : "No"}</div>
                        <div><strong>Year:</strong> ${specs.year ?? "?"}</div>
                    </div>
                </div>
                <p class="result-why">
                    ${(item.why && item.why.length)
                        ? item.why.join(" • ")
                        : "Strong overall match for your preferences"}
                </p>
            `;

            resultsList.appendChild(card);

            // 3D viewer handling (TOP RESULT ONLY)
            if (idx === 0 && item["3d_status_url"]) {
                resultsSummary.textContent = "Generating 3D preview…";
                modelViewer.src = modelViewer.getAttribute("data-default-src");
                poll3DModel(item["3d_status_url"]);
            }
        });

        resultsSummary.textContent = `Top ${items.length} matches • Ranked by relevance`;
    })
    .catch(err => {
        console.error("Recommendation error:", err);
        resultsSummary.textContent = "Error";
        resultsList.innerHTML = `
            <p class="placeholder">
                Something went wrong while retrieving recommendations.
            </p>
        `;
    });
});
