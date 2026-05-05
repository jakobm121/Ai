const fmtPct = (v) => `${Number(v || 0).toFixed(1)}%`;
const fmtUnits = (v) => `${Number(v || 0) >= 0 ? '+' : ''}${Number(v || 0).toFixed(2)}u`;
const fmtNum = (v, d = 2) => Number(v || 0).toFixed(d);

function safeText(v, fallback = '') {
  return v === null || v === undefined || v === '' ? fallback : String(v);
}

function resultBadge(result) {
  const r = (result || 'pending').toLowerCase();
  return `<span class="badge ${r}">${r}</span>`;
}

function typeBadge(type) {
  const t = (type || 'unknown').toLowerCase();
  return `<span class="typeBadge ${t}">${t}</span>`;
}

function numClass(v) {
  return Number(v || 0) >= 0 ? 'good' : 'bad';
}

function renderSummary(summary) {
  const cards = [
    ['Total Picks', summary.total_results || summary.picks || 0],
    ['Settled', summary.settled_picks || summary.settled || 0],
    ['Pending', summary.pending_picks || summary.pending || 0],
    ['Wins', summary.wins || 0],
    ['Hit Rate', fmtPct(summary.hit_rate || 0)],
    ['Profit', fmtUnits(summary.profit || 0)],
    ['ROI', fmtPct(summary.roi || 0)],
    ['Avg Odds', fmtNum(summary.avg_odds || 0, 2)],
  ];

  document.getElementById('summaryCards').innerHTML = cards.map(([label, value]) => `
    <div class="card">
      <span>${label}</span>
      <strong>${value}</strong>
    </div>
  `).join('');
}

function renderCurrentPicks(items) {
  const body = document.getElementById('currentPicksBody');

  if (!items || !items.length) {
    body.innerHTML = `<tr><td colspan="9" class="muted">No current picks yet.</td></tr>`;
    return;
  }

  body.innerHTML = items.map(x => `
    <tr>
      <td>${safeText(x.date)}<br><span class="muted">${safeText(x.time)}</span></td>
      <td>
        <strong>${safeText(x.match)}</strong>
        <br><span class="muted">${safeText(x.tournament)} · ${safeText(x.tour_level)}</span>
      </td>
      <td>
        <strong>${safeText(x.bet)}</strong>
        <br><span class="muted">${safeText(x.best_bookmaker)}</span>
      </td>
      <td>${fmtNum(x.odds, 2)}</td>
      <td>${typeBadge(x.favorite_type)}</td>
      <td class="good">${fmtPct((x.edge || 0) * 100)}</td>
      <td>${fmtNum(x.confidence, 1)}</td>
      <td>${fmtNum(x.stake, 2)}u<br><span class="muted">${safeText(x.stake_label)}</span></td>
      <td>${resultBadge(x.result)}</td>
    </tr>
  `).join('');
}

function renderDaily(rows) {
  const body = document.getElementById('dailyBody');

  if (!rows || !rows.length) {
    body.innerHTML = `<tr><td colspan="10" class="muted">No daily data yet.</td></tr>`;
    return;
  }

  body.innerHTML = rows.map(x => `
    <tr>
      <td><strong>${safeText(x.date)}</strong></td>
      <td>${x.picks || 0}</td>
      <td>${x.settled || 0}</td>
      <td>${x.pending || 0}</td>
      <td>${x.wins || 0}-${x.losses || 0}</td>
      <td>${fmtPct(x.hit_rate || 0)}</td>
      <td>${fmtUnits(x.stake || 0)}</td>
      <td class="${numClass(x.profit)}">${fmtUnits(x.profit || 0)}</td>
      <td class="${numClass(x.roi)}">${fmtPct(x.roi || 0)}</td>
      <td>${fmtNum(x.avg_odds || 0, 2)}</td>
    </tr>
  `).join('');
}

function renderStatsTable(id, rows) {
  const body = document.getElementById(id);

  if (!body) return;

  if (!rows || !rows.length) {
    body.innerHTML = `<tr><td colspan="6" class="muted">No data yet.</td></tr>`;
    return;
  }

  body.innerHTML = rows.map(x => `
    <tr>
      <td><strong>${safeText(x.group)}</strong></td>
      <td>${x.picks || 0}</td>
      <td>${x.settled || 0}</td>
      <td>${fmtPct(x.hit_rate || 0)}</td>
      <td class="${numClass(x.profit)}">${fmtUnits(x.profit || 0)}</td>
      <td class="${numClass(x.roi)}">${fmtPct(x.roi || 0)}</td>
    </tr>
  `).join('');
}

function renderResults(items) {
  const body = document.getElementById('resultsBody');
  const recent = (items || []).slice().reverse().slice(0, 60);

  if (!recent.length) {
    body.innerHTML = `<tr><td colspan="7" class="muted">No results yet.</td></tr>`;
    return;
  }

  body.innerHTML = recent.map(x => `
    <tr>
      <td>${safeText(x.date)}<br><span class="muted">${safeText(x.time)}</span></td>
      <td>
        <strong>${safeText(x.match)}</strong>
        <br><span class="muted">${safeText(x.tournament)} · ${safeText(x.tour_level)}</span>
      </td>
      <td>
        <strong>${safeText(x.bet)}</strong>
        <br>${typeBadge(x.favorite_type)}
      </td>
      <td>${fmtNum(x.odds, 2)}</td>
      <td>${safeText(x.final_score, '-')}</td>
      <td>${resultBadge(x.result)}</td>
      <td class="${numClass(x.profit)}">${isFinite(Number(x.profit)) ? fmtUnits(x.profit) : '-'}</td>
    </tr>
  `).join('');
}

async function main() {
  try {
    const res = await fetch('tennis_site_data.json?ts=' + Date.now());

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();

    document.getElementById('lastUpdate').textContent =
      data.generated_at ? new Date(data.generated_at).toLocaleString() : 'No data yet';

    renderSummary(data.summary || {});
    renderCurrentPicks(data.current_picks || []);
    renderDaily(data.tables?.daily_performance || []);

    renderStatsTable('byFavoriteType', data.tables?.by_favorite_type || []);
    renderStatsTable('byOddsBand', data.tables?.by_odds_band || []);
    renderStatsTable('byConfidence', data.tables?.by_confidence || []);
    renderStatsTable('byStakeLabel', data.tables?.by_stake_label || []);
    renderStatsTable('byTourLevel', data.tables?.by_tour_level || []);
    renderStatsTable('byGender', data.tables?.by_gender || []);

    renderResults(data.results || []);
  } catch (err) {
    console.error(err);

    document.getElementById('lastUpdate').textContent = 'No data yet';
    document.getElementById('summaryCards').innerHTML =
      `<div class="card"><span>Status</span><strong>No data</strong></div>`;
    document.getElementById('currentPicksBody').innerHTML =
      `<tr><td colspan="9" class="muted">Run the GitHub Action first to generate tennis_site_data.json.</td></tr>`;
  }
}

main();
