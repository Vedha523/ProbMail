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
            const rows = document.querySelectorAll(".email-row, .table-row-clickable");
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

    // 6. Start Dashboard Live Polling if dashboard elements exist
    startDashboardLiveUpdates();
});

// Global reference for live Chart update without re-instantiation
window.distributionChartInstance = null;
window.dashboardPollTimer = null;
let isDashboardPolling = false;

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
        if (window.distributionChartInstance) {
            window.distributionChartInstance.destroy();
            window.distributionChartInstance = null;
        }

        const hamCount = parseInt(distCanvas.getAttribute("data-ham") || 0);
        const spamCount = parseInt(distCanvas.getAttribute("data-spam") || 0);

        window.distributionChartInstance = new Chart(distCanvas, {
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
                cutout: "68%",
                animation: {
                    duration: 350
                }
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

/**
 * Escapes HTML characters to prevent XSS during dynamic DOM rendering.
 */
function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Generates HTML for a single email row in the Recent Classifications table.
 */
function renderRecentEmailRow(email) {
    const isSpam = (email.prediction || "").toUpperCase() === "SPAM";
    const badgeHtml = isSpam
        ? '<span class="badge-tag badge-spam">SPAM</span>'
        : '<span class="badge-tag badge-ham">HAM</span>';
    const unreadClass = email.is_read ? "" : " unread";
    const probColor = isSpam ? "#ef4444" : "#10b981";
    const probLabel = isSpam
        ? `${email.spam_probability}% Spam`
        : `${email.ham_probability}% Ham`;
    const snippet = email.body_snippet ? `- ${escapeHtml(email.body_snippet)}...` : "";
    const dateStr = email.created_date || "";
    const viewUrl = email.view_url || `/email/${email.id}`;

    return `
        <tr class="email-row${unreadClass}" data-id="${email.id}" onclick="window.location.href='${viewUrl}'">
            <td class="email-badge-col">${badgeHtml}</td>
            <td class="email-sender-col"><b>${escapeHtml(email.sender_email || "")}</b></td>
            <td class="email-subject-col">
                <span>${escapeHtml(email.subject || "(No Subject)")}</span>
                <span class="email-snippet">${snippet}</span>
            </td>
            <td class="email-prob-col">
                <div class="prob-text">
                    <span style="color: ${probColor}; font-weight: 700;">${probLabel}</span>
                </div>
                <div class="prob-meter-container">
                    <div class="prob-meter-fill" style="width: ${email.spam_probability}%; background-color: ${probColor};"></div>
                </div>
            </td>
            <td class="email-date-col">${dateStr}</td>
        </tr>
    `;
}

/**
 * Updates or re-renders the Recent Classifications table in place without page reload.
 */
function updateRecentEmailsTable(items) {
    const container = document.getElementById("recentEmailsContainer");
    if (!container) return;

    if (!items || items.length === 0) {
        container.innerHTML = `
            <div class="empty-state" id="recentEmailsEmptyState">
                <div class="empty-state-icon">📭</div>
                <div class="empty-state-title">No emails processed yet</div>
                <p>Compose an email or test the classifier to generate operational data.</p>
                <a href="/compose" class="btn-primary" style="margin-top: 14px;">
                    Classify Your First Email
                </a>
            </div>
        `;
        return;
    }

    const tbody = document.getElementById("recentEmailsTbody");
    const countText = document.getElementById("recentEmailsCountText");

    if (tbody) {
        tbody.innerHTML = items.map(renderRecentEmailRow).join("");
        if (countText) {
            countText.textContent = `Showing latest ${items.length} classification record(s)`;
        }
    } else {
        container.innerHTML = `
            <table class="email-table" id="recentEmailsTable">
                <tbody id="recentEmailsTbody">
                    ${items.map(renderRecentEmailRow).join("")}
                </tbody>
            </table>
            <div id="recentEmailsFooter" style="padding: 12px 20px; background: #f8fafc; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--text-muted);">
                <span id="recentEmailsCountText">Showing latest ${items.length} classification record(s)</span>
                <a href="/history" style="font-weight: 600;">View Full History &rarr;</a>
            </div>
        `;
    }
}

/**
 * Updates sidebar badge counts dynamically.
 */
function updateSidebarBadges(counts) {
    if (!counts) return;

    const inboxBadge = document.getElementById("sidebarBadgeInbox");
    if (inboxBadge) {
        const val = counts.inbox_total || 0;
        inboxBadge.textContent = val;
        inboxBadge.style.display = val > 0 ? "" : "none";
    }

    const spamBadge = document.getElementById("sidebarBadgeSpam");
    if (spamBadge) {
        const val = counts.spam_total || 0;
        spamBadge.textContent = val;
        spamBadge.style.display = val > 0 ? "" : "none";
    }

    const sentBadge = document.getElementById("sidebarBadgeSent");
    if (sentBadge) {
        const val = counts.sent_total || 0;
        sentBadge.textContent = val;
        sentBadge.style.display = val > 0 ? "" : "none";
    }
}

/**
 * Updates all Dashboard DOM elements in place using live JSON payload.
 */
function updateDashboardDOM(data) {
    if (!data) return;

    // 1. Update KPI Values
    const totalEl = document.getElementById("kpiTotalProcessed");
    const hamEl = document.getElementById("kpiHamCount");
    const spamEl = document.getElementById("kpiSpamCount");
    const rateEl = document.getElementById("kpiSpamRate");

    if (totalEl) totalEl.textContent = data.total_processed;
    if (hamEl) hamEl.textContent = data.ham_count;
    if (spamEl) spamEl.textContent = data.spam_count;
    if (rateEl) rateEl.textContent = data.spam_rate + "%";

    // 2. Update Distribution Chart dataset and legend numbers
    if (window.distributionChartInstance && window.distributionChartInstance.data) {
        window.distributionChartInstance.data.datasets[0].data = [data.ham_count, data.spam_count];
        window.distributionChartInstance.update();
    }
    const chartHamEl = document.getElementById("chartHamText");
    const chartSpamEl = document.getElementById("chartSpamText");
    if (chartHamEl) chartHamEl.textContent = data.ham_count;
    if (chartSpamEl) chartSpamEl.textContent = data.spam_count;

    // 3. Update Recent Classifications Table
    updateRecentEmailsTable(data.recent_classifications || []);

    // 4. Update Sidebar Badges
    if (data.folder_counts) {
        updateSidebarBadges(data.folder_counts);
    }

    // 5. Update Status Dot & Timestamp
    const liveStatusDot = document.getElementById("liveStatusDot");
    const lastUpdatedTime = document.getElementById("lastUpdatedTime");
    const liveStatusText = document.getElementById("liveStatusText");
    if (liveStatusDot) liveStatusDot.style.backgroundColor = "#10b981";
    if (lastUpdatedTime) {
        lastUpdatedTime.textContent = data.timestamp || new Date().toLocaleTimeString();
    }
    if (liveStatusText && !lastUpdatedTime) {
        liveStatusText.textContent = "Live • Synced " + (data.timestamp || "");
    }
}

/**
 * Fetches the latest stats from /api/dashboard-stats and refreshes the Dashboard.
 */
window.refreshDashboardData = function (callback) {
    if (isDashboardPolling) return;
    isDashboardPolling = true;

    let url = "/api/dashboard-stats";
    const savedToken = localStorage.getItem("probmail_token");
    if (savedToken) {
        url += "?token=" + encodeURIComponent(savedToken);
    }

    fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => {
        if (!res.ok) throw new Error("HTTP error " + res.status);
        return res.json();
    })
    .then(data => {
        isDashboardPolling = false;
        if (data && data.success) {
            updateDashboardDOM(data);
            if (typeof callback === "function") callback(data);
        }
    })
    .catch(err => {
        isDashboardPolling = false;
        // Subtle error/reconnecting state: preserve last valid data and retry on next interval
        const liveStatusDot = document.getElementById("liveStatusDot");
        const liveStatusText = document.getElementById("liveStatusText");
        if (liveStatusDot) liveStatusDot.style.backgroundColor = "#f59e0b";
        if (liveStatusText) {
            liveStatusText.innerHTML = 'Connecting... <span style="font-size:10px;">(Retaining data)</span>';
        }
        if (typeof callback === "function") callback(null, err);
    });
};

/**
 * Starts automatic polling every 4 seconds while the dashboard is active.
 * Cleans up on tab hide/switch and page unload.
 */
function startDashboardLiveUpdates() {
    const isDashboard = document.getElementById("kpiTotalProcessed") || document.getElementById("distributionChart");
    if (!isDashboard) return;

    if (window.dashboardPollTimer) {
        clearInterval(window.dashboardPollTimer);
        window.dashboardPollTimer = null;
    }

    const POLL_INTERVAL = 4000;
    window.dashboardPollTimer = setInterval(() => {
        if (!document.hidden) {
            window.refreshDashboardData();
        }
    }, POLL_INTERVAL);

    // Clean up timer on page unload
    window.addEventListener("beforeunload", () => {
        if (window.dashboardPollTimer) {
            clearInterval(window.dashboardPollTimer);
            window.dashboardPollTimer = null;
        }
    });

    // Pause polling when browser tab is inactive, resume immediately when visible
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            if (window.dashboardPollTimer) {
                clearInterval(window.dashboardPollTimer);
                window.dashboardPollTimer = null;
            }
        } else {
            window.refreshDashboardData();
            if (!window.dashboardPollTimer) {
                window.dashboardPollTimer = setInterval(() => {
                    if (!document.hidden) {
                        window.refreshDashboardData();
                    }
                }, POLL_INTERVAL);
            }
        }
    });
}

