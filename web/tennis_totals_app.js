const SITE_DATA_URL = "tennis_totals_site_data.json";

const fmt = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
});

function num(v, fallback = 0) {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}

function pct(v) {
  if (!Number.isFinite(v)) return "-";
  return `${fmt.format(v * 100)}%`;
}

function money(v) {
  const n = num(v);
  const cls = n >= 0 ? "good" : "bad";
  const sign = n > 0 ? "+" : "";
  return `<span class="${cls}">${sign}${fmt.format(n)}</span>`;
}

function resultBadge(result) {
  const r = String(result || "pending").toLowerCase();
  return `<span class="badge ${r}">${r}</span>`;
}

function sideBadge(side) {
  const s = String(side || "unknown").toLowerCase();
  return `<span class="typeBadge ${s === "over" ? "favorite" : s === "under" ? "underdog" : "unknown"}">${s}</span>`;
}

function edgeText(edge) {
  const e = num(edge);
  return e >= 0 ? `<span class="good">+${fmt.format(e * 100)}%</span>` : `<span class="bad">${fmt.format(e * 100)}%</span>`;
}

function roi(profit, stake) {
  const s = num(stake);
  if (s <= 0) return 0;
  return num(profit) / s;
}

function groupStats(items) {
  const picks = items.length;
  const settledItems = items.filter(x => ["win", "loss"].includes(String(x.result || "").toLowerCase()));
  const settled = settledItems.length;
  const pending = picks - settled;
  const wins = settledItems.filter(x => String(x.result).toLowerCase() === "win").length;
  const losses = settledItems.filter(x => String(x.result).toLowerCase() === "loss").length;
  const stake = settledItems.reduce((a, x) => a + num(x.stake), 0);
  const profit = settledItems.reduce((a, x) => a + num(x.profit), 0);
  const avgOdds = settledItems.length
    ? settledItems.reduce((a, x) => a + num(x.odds), 0) / settledItems.length
    : 0;

  return {
    picks,
    settled,
    pending,
    wins,
    losses,
    stake,
    profit,
    hitRate: settled ? wins / settled : 0,
    roi: roi(profit, stake),
    avgOdds,
  };
}

function renderSummary(predictions, results) {
  const all = Array.isArray(results) ? results : [];
  const current = Array.isArray(predictions?.picks) ? predictions.picks : [];
  const stats = groupStats(all);

  const pending = all.filter(x => String(x.result || "pending").toLowerCase() === "pending").length;
  const settled = stats.settled;

  const cards = [
    ["Current", current.length],
    ["All Picks", stats.picks],
    ["Settled", settled],
    ["Pending", pending],
    ["W-L", `${stats.wins}-${stats.losses}`],
    ["Hit Rate", pct(stats.hitRate)],
    ["Profit", `${stats.profit >= 0 ? "+" : ""}${fmt.format(stats.profit)}`],
    ["ROI", pct(stats.roi)],
  ];

  document.getElementById("summaryCards").innerHTML = cards.map(([label, value]) => `
    <article class="card">
      <span>${label}</span>
      <strong>${value}</strong>
    </article>
  `).join("");
}

function renderCurrent(predictions) {
  const picks = Array.isArray(predictions?.picks) ? predictions.picks : [];
  const body = document.getElementById("currentPicksBody");

  if (!picks.length) {
    body.innerHTML = `<tr><td colspan="10" class="muted">No current totals picks.</td></tr>`;
    return;
  }

  body.innerHTML = picks.map(p => `
    <tr>
      <td>
        <strong>${p.date || "-"}</strong><br>
        <span class="muted">${p.time || ""}</span>
      </td>
      <td>
        <strong>${p.match || "-"}</strong><br>
        <span class="muted">${p.tournament || ""}</span>
      </td>
      <td>
        <strong>${p.bet || "-"}</strong><br>
        <span class="muted">Exp: ${fmt.format(num(p.expected_total_games))}</span>
      </td>
      <td>${fmt.format(num(p.line))}</td>
      <td>
        <strong>${fmt.format(num(p.odds))}</strong><br>
        <span class="muted">${p.best_bookmaker || ""}</span>
      </td>
      <td>${sideBadge(p.side)}</td>
      <td>${edgeText(p.edge)}</td>
      <td>${fmt.format(num(p.confidence))}</td>
      <td>
        <strong>${fmt.format(num(p.stake))}</strong><br>
        <span class="muted">${p.stake_label || ""}</span>
      </td>
      <td>${resultBadge(p.result)}</td>
    </tr>
  `).join("");
}

function renderDaily(results) {
  const body = document.getElementById("dailyBody");
  const all = Array.isArray(results) ? results : [];

  if (!all.length) {
    body.innerHTML = `<tr><td colspan="10" class="muted">No totals history yet.</td></tr>`;
    return;
  }

  const byDate = new Map();

  for (const p of all) {
    const key = p.date || "unknown";
    if (!byDate.has(key)) byDate.set(key, []);
    byDate.get(key).push(p);
  }

  const rows = [...byDate.entries()]
    .sort((a, b) => String(b[0]).localeCompare(String(a[0])))
    .map(([date, items]) => {
      const s = groupStats(items);
      return `
        <tr>
          <td><strong>${date}</strong></td>
          <td>${s.picks}</td>
          <td>${s.settled}</td>
          <td>${s.pending}</td>
          <td>${s.wins}-${s.losses}</td>
          <td>${pct(s.hitRate)}</td>
          <td>${fmt.format(s.stake)}</td>
          <td>${money(s.profit)}</td>
          <td>${pct(s.roi)}</td>
          <td>${s.avgOdds ? fmt.format(s.avgOdds) : "-"}</td>
        </tr>
      `;
    });

  body.innerHTML = rows.join("");
}

function oddsBand(p) {
  const o = num(p.odds);
  if (o < 1.75) return "1.65 - 1.74";
  if (o < 1.90) return "1.75 - 1.89";
  if (o < 2.05) return "1.90 - 2.04";
  return "2.05+";
}

function confidenceBand(p) {
  const c = num(p.confidence);
  if (c >= 90) return "90+";
  if (c >= 82) return "82 - 89";
  if (c >= 74) return "74 - 81";
  return "<74";
}

function lineBand(p) {
  const l = num(p.line);
  if (l <= 19.5) return "18.5 - 19.5";
  if (l <= 21.5) return "20.0 - 21.5";
  if (l <= 22.5) return "22.0 - 22.5";
  return "23.0+";
}

function renderGroupTable(elementId, results, grouper) {
  const body = document.getElementById(elementId);
  const all = Array.isArray(results) ? results : [];
  const map = new Map();

  for (const p of all) {
    const key = grouper(p) || "unknown";
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(p);
  }

  if (!map.size) {
    body.innerHTML = `<tr><td colspan="6" class="muted">No data yet.</td></tr>`;
    return;
  }

  body.innerHTML = [...map.entries()]
    .sort((a, b) => String(a[0]).localeCompare(String(b[0])))
    .map(([group, items]) => {
      const s = groupStats(items);
      return `
        <tr>
          <td><strong>${group}</strong></td>
          <td>${s.picks}</td>
          <td>${s.settled}</td>
          <td>${pct(s.hitRate)}</td>
          <td>${money(s.profit)}</td>
          <td>${pct(s.roi)}</td>
        </tr>
      `;
    }).join("");
}

function renderResults(results) {
  const body = document.getElementById("resultsBody");
  const all = Array.isArray(results) ? results : [];

  if (!all.length) {
    body.innerHTML = `<tr><td colspan="8" class="muted">No totals results yet.</td></tr>`;
    return;
  }

  const rows = [...all]
    .sort((a, b) => {
      const ad = `${a.date || ""} ${a.time || ""}`;
      const bd = `${b.date || ""} ${b.time || ""}`;
      return bd.localeCompare(ad);
    })
    .slice(0, 80)
    .map(p => `
      <tr>
        <td>
          <strong>${p.date || "-"}</strong><br>
          <span class="muted">${p.time || ""}</span>
        </td>
        <td>
          <strong>${p.match || "-"}</strong><br>
          <span class="muted">${p.tournament || ""}</span>
        </td>
        <td>
          <strong>${p.bet || "-"}</strong><br>
          <span class="muted">Line ${fmt.format(num(p.line))}</span>
        </td>
        <td>${fmt.format(num(p.odds))}</td>
        <td>${p.total_games ?? "-"}</td>
        <td>${p.final_score || "-"}</td>
        <td>${resultBadge(p.result)}</td>
        <td>${p.profit === undefined ? "-" : money(p.profit)}</td>
      </tr>
    `);

  body.innerHTML = rows.join("");
}

async function init() {
  try {
    const res = await fetch(`${SITE_DATA_URL}?v=${Date.now()}`);

    if (!res.ok) {
      throw new Error(`Failed to load ${SITE_DATA_URL}`);
    }

    const data = await res.json();

    const predictions = data.predictions || {};
    const results = Array.isArray(data.results) ? data.results : [];

    document.getElementById("lastUpdate").textContent =
      predictions.generated_at || data.built_at || "Unknown";

    renderSummary(predictions, results);
    renderCurrent(predictions);
    renderDaily(results);

    renderGroupTable("bySide", results, p => String(p.side || "unknown").toUpperCase());
    renderGroupTable("byOddsBand", results, oddsBand);
    renderGroupTable("byConfidence", results, confidenceBand);
    renderGroupTable("byStakeLabel", results, p => p.stake_label || "unknown");
    renderGroupTable("byTourLevel", results, p => p.tour_level || "unknown");
    renderGroupTable("byLineBand", results, lineBand);

    renderResults(results);
  } catch (err) {
    console.error(err);

    document.getElementById("lastUpdate").textContent = "Error";
    document.getElementById("summaryCards").innerHTML = `
      <article class="card">
        <span>Error</span>
        <strong>Could not load totals data</strong>
      </article>
    `;
  }
}

init();
