const fmtPct = (v) => `${Number(v || 0).toFixed(1)}%`;
const fmtUnits = (v) => `${Number(v || 0) >= 0 ? '+' : ''}${Number(v || 0).toFixed(2)}u`;

function badge(result) {
  const r = (result || 'pending').toLowerCase();
  return `<span class="badge ${r}">${r}</span>`;
}

function rowClassNum(value) {
  return Number(value || 0) >= 0 ? 'good' : 'bad';
}

function renderSummary(summary) {
  const cards = [
    ['Settled', summary.settled_picks || 0],
    ['Pending', summary.pending_picks || 0],
    ['Wins', summary.wins || 0],
    ['Hit Rate', fmtPct(summary.hit_rate || 0)],
    ['Accuracy ROI', fmtPct(summary.roi_accuracy_mode || summary.roi || 0)],
  ];

  document.getElementById('summaryCards').innerHTML = cards.map(([k, v]) => `
    <div class="card"><span>${k}</span><strong>${v}</strong></div>
  `).join('');
}

function renderPredictions(items) {
  const body = document.getElementById('predictionsBody');

  if (!items || !items.length) {
    body.innerHTML = `<tr><td colspan="8" class="muted">No current predictions yet.</td></tr>`;
    return;
  }

  body.innerHTML = items.map(x => `
    <tr>
      <td>${x.date || ''}<br><span class="muted">${x.time || ''}</span></td>
      <td><strong>${x.match || ''}</strong><br><span class="muted">${x.league || ''}</span></td>
      <td>${x.bet || x.pick_team || ''}</td>
      <td>BO${x.best_of || ''}</td>
      <td>${fmtPct((x.model_prob || 0) * 100)}</td>
      <td>${Number(x.confidence || 0).toFixed(1)}</td>
      <td>${x.tier || 'unknown'}</td>
      <td>${badge(x.result)}</td>
    </tr>
  `).join('');
}

function renderStatsTable(id, rows) {
  const body = document.getElementById(id);

  if (!body) return;

  if (!rows || !rows.length) {
    body.innerHTML = `<tr><td colspan="5" class="muted">No settled data yet.</td></tr>`;
    return;
  }

  body.innerHTML = rows.map(x => {
    const profit = x.profit_units ?? x.profit ?? 0;

    return `
      <tr>
        <td>${x.group || 'Unknown'}</td>
        <td>${x.picks || 0}</td>
        <td>${fmtPct(x.hit_rate || 0)}</td>
        <td class="${rowClassNum(profit)}">${fmtUnits(profit)}</td>
        <td class="${rowClassNum(x.roi || 0)}">${fmtPct(x.roi || 0)}</td>
      </tr>
    `;
  }).join('');
}

function renderResults(items) {
  const body = document.getElementById('resultsBody');
  const recent = (items || []).slice().reverse().slice(0, 40);

  if (!recent.length) {
    body.innerHTML = `<tr><td colspan="6" class="muted">No results yet.</td></tr>`;
    return;
  }

  body.innerHTML = recent.map(x => `
    <tr>
      <td>${x.date || ''}<br><span class="muted">${x.time || ''}</span></td>
      <td><strong>${x.match || ''}</strong><br><span class="muted">${x.league || ''}</span></td>
      <td>${x.bet || x.pick_team || ''}</td>
      <td>${x.final_score || '-'}</td>
      <td>${badge(x.result)}</td>
      <td>${Number(x.confidence || 0).toFixed(1)}</td>
    </tr>
  `).join('');
}

function normalizeTableRows(rows) {
  return (rows || []).map(x => ({
    group: x.group || 'Unknown',
    picks: x.picks || 0,
    hit_rate: x.hit_rate || 0,
    profit_units: x.profit_units ?? x.profit ?? 0,
    roi: x.roi || 0,
  }));
}

async function main() {
  try {
    const res = await fetch('cs2_site_data.json?ts=' + Date.now());

    if (!res.ok) {
      throw new Error(`Could not load cs2_site_data.json: HTTP ${res.status}`);
    }

    const data = await res.json();

    document.getElementById('lastUpdate').textContent =
      data.generated_at ? new Date(data.generated_at).toLocaleString() : 'No data yet';

    const summary = data.summary || {};

    renderSummary({
      settled_picks: summary.settled_picks || 0,
      pending_picks: summary.pending_picks || 0,
      wins: summary.wins || 0,
      hit_rate: summary.hit_rate || 0,
      roi_accuracy_mode: summary.roi_accuracy_mode ?? summary.roi ?? 0,
    });

    renderPredictions(
      data.current_picks ||
      data.predictions ||
      data.picks ||
      []
    );

    renderStatsTable(
      'byConfidence',
      normalizeTableRows(data.performance_by_confidence || data.tables?.by_confidence || [])
    );

    renderStatsTable(
      'byBestOf',
      normalizeTableRows(data.performance_by_best_of || data.tables?.by_best_of || [])
    );

    renderStatsTable(
      'byTier',
      normalizeTableRows(data.performance_by_tier || data.tables?.by_tier || [])
    );

    renderStatsTable(
      'byRegion',
      normalizeTableRows(data.performance_by_region || data.tables?.by_region || [])
    );

    renderResults(data.results || []);
  } catch (err) {
    console.error(err);

    document.getElementById('lastUpdate').textContent = 'No data yet';
    document.getElementById('summaryCards').innerHTML =
      `<div class="card"><span>Status</span><strong>No data</strong></div>`;
    document.getElementById('predictionsBody').innerHTML =
      `<tr><td colspan="8" class="muted">Run the GitHub Action first to generate cs2_site_data.json.</td></tr>`;
  }
}

main();
