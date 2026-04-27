const sportIcons = { football: "⚽", basketball: "🏀", tennis: "🎾", hockey: "🏒", baseball: "⚾" };
const AFFILIATE_URL = "reviews.html";
let profitChartInstance = null;
function capitalize(text){ return (!text || typeof text !== "string") ? "" : text.charAt(0).toUpperCase() + text.slice(1); }
function safeNumber(value, fallback = 0){ const n = Number(value); return Number.isFinite(n) ? n : fallback; }
function getConfidenceData(conf){
  const c = safeNumber(conf);
  if (c < 60) return { label: "Signal Stable", units: "Pulse 1.0", color: "#f59e0b" };
  if (c < 75) return { label: "Signal Strong", units: "Pulse 1.5", color: "#22d3ee" };
  return { label: "Signal Elite", units: "Pulse 2.0", color: "#8b5cf6" };
}
function getKickoffStatus(dateStr, timeStr){
  if (!dateStr || !timeStr) return "";
  const [year, month, day] = dateStr.split("-").map(Number);
  const [hours, minutes] = timeStr.split(":").map(Number);
  const now = new Date();
  const matchTime = new Date(year, month - 1, day, hours, minutes, 0, 0);
  const diffMinutes = Math.floor((matchTime - now) / 60000);
  if (diffMinutes <= 0) return "";
  if (diffMinutes < 60) return `⏰ Starts in ${diffMinutes} min`;
  if (diffMinutes < 180) return `🕒 Starts in ${Math.floor(diffMinutes / 60)}h`;
  return "";
}
async function loadPredictions(){
  try{
    const response = await fetch("./predictions.json", { cache: "no-store" });
    const predictions = await response.json();
    renderPredictions(Array.isArray(predictions) ? predictions : []);
    const now = new Date();
    const formatted = now.toLocaleDateString("en-GB") + " • " + now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const el = document.getElementById("last-updated");
    if (el) el.textContent = `Updated • ${formatted}`;
  }catch(e){
    const container = document.getElementById("predictions-container");
    if (container) container.innerHTML = '<article class="prediction-card"><p>Predictions are temporarily unavailable.</p></article>';
  }
}
function renderPredictions(data){
  const container = document.getElementById("predictions-container");
  if (!container) return;
  container.innerHTML = "";
  if (!data.length){ container.innerHTML = '<article class="prediction-card"><p>No predictions available right now.</p></article>'; return; }
  data.forEach((p, index) => {
    const confidenceValue = safeNumber(p.confidence);
    const conf = getConfidenceData(confidenceValue);
    const kickoff = getKickoffStatus(p.date, p.time);
    const sport = capitalize(p.sport || "sport");
    const icon = sportIcons[p.sport] || "🎯";
    const odds = safeNumber(p.odds, null);
    const card = document.createElement("article");
    card.className = "prediction-card";
    card.innerHTML = `
      <div class="prediction-meta">
        <span>📅 ${p.date || "-"}</span>
        <span>🕒 ${p.time || "-"}</span>
        <span>${icon} ${sport}</span>
        <span>🏆 ${p.league || "-"}</span>
      </div>
      <h3>${p.match || "Unknown match"}</h3>
      <p><strong>Tip:</strong> ${p.bet || "-"}</p>
      ${odds ? `<p><strong>Odds:</strong> ${odds.toFixed(2)}</p>` : ""}
      ${kickoff ? `<p class="metric-badge">${kickoff}</p>` : ""}
      <div class="panel-soft"><p><strong>AI Analysis:</strong> ${p.reasoning || "No analysis available."}</p></div>
      <div class="chart-ring"><canvas id="chart${index}" aria-label="Confidence chart"></canvas></div>
      <p class="rating-stars" style="text-align:center">${conf.label} • ${conf.units}</p>
      <a href="${AFFILIATE_URL}" class="btn btn--primary">Check Best Bonus Route</a>
    `;
    container.appendChild(card);
    const chartCanvas = document.getElementById(`chart${index}`);
    if (chartCanvas) {
      new Chart(chartCanvas, {
        type: "doughnut",
        data: { datasets: [{ data: [confidenceValue, Math.max(0, 100 - confidenceValue)], backgroundColor: [conf.color, "#24304f"], borderWidth: 0 }] },
        options: { cutout: "78%", responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { enabled: false } } }
      });
    }
  });
}
async function loadStats(){
  try{
    const res = await fetch("./results.json", { cache: "no-store" });
    const data = await res.json();
    if (!Array.isArray(data)) return;
    let total = 0, wins = 0, profit = 0, totalStaked = 0, avgOddsSum = 0, avgOddsCount = 0;
    const dailyProfit = {};
    data.forEach((p) => {
      if (p.result === "pending") return;
      let units = 1;
      if (safeNumber(p.confidence) >= 75) units = 2;
      else if (safeNumber(p.confidence) >= 60) units = 1.5;
      total++;
      if (typeof p.odds === "number") { avgOddsSum += p.odds; avgOddsCount++; }
      let pickProfit = 0;
      if (p.result === "win") { wins++; totalStaked += units; pickProfit = typeof p.odds === "number" ? (p.odds - 1) * units : units; }
      else if (p.result === "loss") { totalStaked += units; pickProfit = -units; }
      profit += pickProfit;
      const dateKey = p.date || "Unknown";
      if (!dailyProfit[dateKey]) dailyProfit[dateKey] = 0;
      dailyProfit[dateKey] += pickProfit;
    });
    const roi = totalStaked > 0 ? ((profit / totalStaked) * 100).toFixed(1) : "0.0";
    const avgOdds = avgOddsCount > 0 ? (avgOddsSum / avgOddsCount).toFixed(2) : "0.00";
    const statBoxes = document.querySelectorAll(".stat-number");
    if (statBoxes.length >= 4 && total > 0) {
      statBoxes[0].textContent = total;
      statBoxes[1].textContent = wins;
      statBoxes[2].textContent = avgOdds;
      statBoxes[3].textContent = `${roi}%`;
    }
    const profitCanvas = document.getElementById("profitChart");
    if (!profitCanvas) return;
    const sortedDates = Object.keys(dailyProfit).sort();
    let runningProfit = 0;
    const labels = [], values = [];
    sortedDates.forEach((date) => { runningProfit += dailyProfit[date]; labels.push(date); values.push(Number(runningProfit.toFixed(2))); });
    if (profitChartInstance) profitChartInstance.destroy();
    profitChartInstance = new Chart(profitCanvas.getContext("2d"), {
      type: "line",
      data: { labels, datasets: [{ label: "Growth (Units)", data: values, borderColor: "#22d3ee", backgroundColor: "rgba(34, 211, 238, 0.12)", borderWidth: 3, tension: 0.3, fill: true, pointRadius: 0, pointHoverRadius: 4 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: "#b8bfd3" }, grid: { color: "rgba(255,255,255,0.08)" } }, y: { ticks: { color: "#b8bfd3" }, grid: { color: "rgba(255,255,255,0.08)" } } } }
    });
  }catch(e){}
}
document.addEventListener("DOMContentLoaded", () => { loadPredictions(); loadStats(); });
