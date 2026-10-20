/**
 * script.js
 * ---------
 * Vanilla JavaScript for ProbMail.
 * 
 * Features:
 * - Dynamic Chart.js dashboard charts
 * - Client-side email table search filter
 * - Interactive Viva Bayes' Theorem single-word probability calculator
 * - Auto-dismiss flash notifications
 * 
 * Author: 2nd-Year B.Tech Computer Science Student Project
 */

document.addEventListener("DOMContentLoaded", function () {
    // 0. Synchronize and preserve auth token across iframe navigation
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get("token");
    if (urlToken) {
        localStorage.setItem("probmail_token", urlToken);
    }
    const savedToken = localStorage.getItem("probmail_token");

    // If we have a saved token, append it to all internal links so session never drops in iframes
    if (savedToken) {
        document.querySelectorAll("a").forEach(link => {
            const href = link.getAttribute("href");
            if (href && href.startsWith("/") && !href.startsWith("/logout") && !href.includes("token=")) {
                const sep = href.includes("?") ? "&" : "?";
                link.setAttribute("href", href + sep + "token=" + encodeURIComponent(savedToken));
            }
        });

        // Also inject into forms
        document.querySelectorAll("form").forEach(form => {
            if (!form.querySelector('input[name="token"]')) {
                const hiddenInput = document.createElement("input");
                hiddenInput.type = "hidden";
                hiddenInput.name = "token";
                hiddenInput.value = savedToken;
                form.appendChild(hiddenInput);
            }
        });
    }

    // Clear token on logout
    document.querySelectorAll('a[href*="/logout"]').forEach(btn => {
        btn.addEventListener("click", () => {
            localStorage.removeItem("probmail_token");
        });
    });

    // 1. Auto-dismiss flash messages after 5 seconds
    const flashes = document.querySelectorAll(".flash-message");
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.transition = "opacity 0.5s ease";
            flash.style.opacity = "0";
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    });

    // 2. Client-side search filtering on email lists
    const liveSearchInput = document.getElementById("liveSearchInput");
    if (liveSearchInput) {
        liveSearchInput.addEventListener("input", function (e) {
            const query = e.target.value.toLowerCase().trim();
            const rows = document.querySelectorAll(".email-row");
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        });
    }

    // 3. Make email rows clickable
    const emailRows = document.querySelectorAll(".email-row");
    emailRows.forEach(row => {
        row.addEventListener("click", function (e) {
            // Avoid triggering if clicked on an action button or checkbox inside row
            if (e.target.tagName !== "BUTTON" && e.target.tagName !== "A" && e.target.tagName !== "INPUT") {
                const emailId = this.getAttribute("data-id");
                if (emailId) {
                    window.location.href = `/email/${emailId}`;
                }
            }
        });
    });

    // 4. Initialize Dashboard Charts if canvas elements exist
    initDashboardCharts();

    // 5. Initialize Interactive Bayes Calculator if on statistics/dashboard page
    initBayesCalculator();
});

/**
 * Initializes Chart.js visualization widgets on the dashboard.
 */
function initDashboardCharts() {
    // Check if Chart.js is loaded
    if (typeof Chart === "undefined") {
        return;
    }

    // Chart 1: Distribution Doughnut Chart
    const distCanvas = document.getElementById("distributionChart");
    if (distCanvas) {
        const hamCount = parseInt(distCanvas.getAttribute("data-ham") || 0);
        const spamCount = parseInt(distCanvas.getAttribute("data-spam") || 0);

        new Chart(distCanvas, {
            type: "doughnut",
            data: {
                labels: ["Legitimate (Ham)", "Spam"],
                datasets: [{
                    data: [hamCount, spamCount],
                    backgroundColor: ["#10B981", "#EF4444"],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { font: { size: 12, weight: 600 }, padding: 16 }
                    }
                },
                cutout: "68%"
            }
        });
    }

    // Chart 2: Model Performance Metrics Radar or Bar Chart
    const metricsCanvas = document.getElementById("metricsBarChart");
    if (metricsCanvas) {
        const acc = parseFloat(metricsCanvas.getAttribute("data-acc") || 0);
        const prec = parseFloat(metricsCanvas.getAttribute("data-prec") || 0);
        const rec = parseFloat(metricsCanvas.getAttribute("data-rec") || 0);
        const f1 = parseFloat(metricsCanvas.getAttribute("data-f1") || 0);

        new Chart(metricsCanvas, {
            type: "bar",
            data: {
                labels: ["Accuracy", "Precision", "Recall", "F1 Score"],
                datasets: [{
                    label: "Evaluation Metric (%)",
                    data: [acc, prec, rec, f1],
                    backgroundColor: [
                        "rgba(37, 99, 235, 0.8)",
                        "rgba(16, 185, 129, 0.8)",
                        "rgba(245, 158, 11, 0.8)",
                        "rgba(139, 92, 246, 0.8)"
                    ],
                    borderColor: ["#2563EB", "#10B981", "#F59E0B", "#8B5CF6"],
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: v => v + "%" },
                        grid: { color: "#f1f5f9" }
                    },
                    x: { grid: { display: false } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}

/**
 * Interactive Bayes Calculator for viva presentation.
 * Allows the student to type any test word and query its exact conditional probability.
 */
function initBayesCalculator() {
    const calcInput = document.getElementById("bayesCalcInput");
    const calcBtn = document.getElementById("bayesCalcBtn");
    const calcResult = document.getElementById("bayesCalcResult");

    if (!calcBtn || !calcInput || !calcResult) return;

    calcBtn.addEventListener("click", function () {
        const word = calcInput.value.trim().toLowerCase();
        if (!word) return;

        calcResult.innerHTML = "<span style='color: #64748b;'>Calculating Bayesian probability...</span>";

        fetch(`/api/bayes-word-probability?word=${encodeURIComponent(word)}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    calcResult.innerHTML = `<span style="color:#ef4444;">${data.error}</span>`;
                    return;
                }

                const spamPct = (data.p_spam_given_word * 100).toFixed(2);
                const hamPct = (data.p_ham_given_word * 100).toFixed(2);
                const badgeClass = data.p_spam_given_word >= 0.5 ? "badge-spam" : "badge-ham";
                const verdict = data.p_spam_given_word >= 0.5 ? "SPAM LEANING" : "HAM LEANING";

                calcResult.innerHTML = `
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-top:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <span style="font-weight:700; font-size:15px; color:#0f172a;">Target Word: <span class="code-pill">${data.word}</span></span>
                            <span class="badge-tag ${badgeClass}">${verdict}</span>
                        </div>
                        <div style="font-family:monospace; font-size:13px; color:#334155; margin-bottom:12px; background:#f8fafc; padding:8px 12px; border-radius:6px;">
                            P(Spam | "${data.word}") = <b>${spamPct}%</b> &nbsp;|&nbsp; P(Ham | "${data.word}") = <b>${hamPct}%</b>
                        </div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:12px; color:#64748b;">
                            <div>• P("${data.word}" | Spam) Likelihood: <b>${data.p_word_given_spam}</b></div>
                            <div>• P("${data.word}" | Ham) Likelihood: <b>${data.p_word_given_ham}</b></div>
                            <div>• Training Spam Occurrences: <b>${data.spam_count_in_train}</b></div>
                            <div>• Training Ham Occurrences: <b>${data.ham_count_in_train}</b></div>
                        </div>
                    </div>
                `;
            })
            .catch(err => {
                calcResult.innerHTML = `<span style="color:#ef4444;">Failed to calculate: ${err}</span>`;
            });
    });
}
