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
// Safe 3D Polling (Fixed SyntaxError)
// -------------------------
function poll3DModel(statusUrl) {
    console.log("Starting 3D poll:", statusUrl);  // Debug
    const interval = setInterval(async () => {
        try {
            const res = await fetch(statusUrl);
            if (!res.ok) {
                console.warn("3D status non-OK:", res.status);
                return;
            }

            const text = await res.text();  // Fix: .text() first to catch HTML errors
            console.log("Raw 3D response:", text.substring(0, 100));  // Debug raw

            let data;
            try {
                data = JSON.parse(text);
            } catch (parseErr) {
                console.error("JSON parse failed:", parseErr, "Raw:", text);
                return;  // Skip invalid JSON (prevents Safari SyntaxError)
            }

            if (data.status === "ready" && data.model_url) {
                modelViewer.src = data.model_url;
                resultsSummary.textContent = "3D model ready!";
                clearInterval(interval);
            } else if (data.status === "error") {
                console.error("3D error:", data.message);
                clearInterval(interval);
            }
        } catch (err) {
            console.error("3D polling failed:", err);
            clearInterval(interval);
        }
    }, 3000);
}

// -------------------------
// Form submit (Updated API paths)
// -------------------------
form.addEventListener("submit", function (e) {
    e.preventDefault();

    resultsSummary.textContent = "Analyzing your preferences…";
    resultsList.innerHTML = `<p class="placeholder">Running recommendation engine…</p>`;

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    // Fix: New /api/ paths from updated urls.py
    fetch("/recommend/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(payload)
    })
    .then(async res => {
        if (!res.ok) throw new Error("HTTP " + res.status);

        const text = await res.text();  // Safe: text first
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error("Recommend JSON failed:", text.substring(0, 200));
            throw new Error("Invalid server response");
        }
        return data;
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
                    <!-- Fix: Dynamic image_url from backend -->
                    <img src="${item.image_url || '/media/placeholder.png'}" class="result-image" alt="${item.model}" onerror="this.src='/media/placeholder.png'">
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
                    ${(item.why && item.why.length) ? item.why.join(" • ") : "Strong overall match for your preferences"}
                </p>
            `;
            resultsList.appendChild(card);

            // 3D viewer (TOP RESULT ONLY) - Fixed path
            if (idx === 0 && item["3d_status_url"]) {
                resultsSummary.textContent = "Generating 3D preview…";
                modelViewer.src = modelViewer.getAttribute("data-default-src") || "";
                poll3DModel(item["3d_status_url"]);
            }
        });

        resultsSummary.textContent = `Top ${items.length} matches • Ranked by relevance`;
    })
    .catch(err => {
        console.error("Recommendation error:", err);
        resultsSummary.textContent = "Error occurred";
        resultsList.innerHTML = `
            <p class="placeholder">
                Connection issue. Check console for details.<br>
                <small>Server: /api/recommend/ | 3D: /api/3d-status/</small>
            </p>
        `;
    });
});
