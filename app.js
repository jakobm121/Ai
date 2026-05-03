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
    ['Settled', summary.settled_picks],
    ['Pending', summary.pending_picks],
    ['Wins', summary.wins],
    ['Hit Rate', fmtPct(summary.hit_rate)],
    ['Accuracy ROI', fmtPct(summary.roi_accuracy_mode)],
  ];
  document.getElementById('summaryCards').innerHTML = cards.map(([k,v]) => `
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
      <td>${x.bet || ''}</td>
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
  if (!rows || !rows.length) {
    body.innerHTML = `<tr><td colspan="5" class="muted">No settled data yet.</td></tr>`;
    return;
  }
  body.innerHTML = rows.map(x => `
    <tr>
      <td>${x.group}</td>
      <td>${x.picks}</td>
      <td>${fmtPct(x.hit_rate)}</td>
      <td class="${rowClassNum(x.profit_units)}">${fmtUnits(x.profit_units)}</td>
      <td class="${rowClassNum(x.roi)}">${fmtPct(x.roi)}</td>
    </tr>
  `).join('');
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
      <td>${x.bet || ''}</td>
      <td>${x.final_score || '-'}</td>
      <td>${badge(x.result)}</td>
      <td>${Number(x.confidence || 0).toFixed(1)}</td>
    </tr>
  `).join('');
}

async function main() {
  try {
    const res = await fetch('cs2_data.json?ts=' + Date.now());
    const data = await res.json();
    document.getElementById('lastUpdate').textContent = new Date(data.generated_at).toLocaleString();
    renderSummary(data.summary || {});
    renderPredictions(data.predictions || []);
    renderStatsTable('byConfidence', data.tables?.by_confidence || []);
    renderStatsTable('byBestOf', data.tables?.by_best_of || []);
    renderStatsTable('byTier', data.tables?.by_tier || []);
    renderStatsTable('byRegion', data.tables?.by_region || []);
    renderResults(data.results || []);
  } catch (err) {
    document.getElementById('lastUpdate').textContent = 'No data yet';
    document.getElementById('summaryCards').innerHTML = `<div class="card"><span>Status</span><strong>No data</strong></div>`;
    document.getElementById('predictionsBody').innerHTML = `<tr><td colspan="8" class="muted">Run the GitHub Action first to generate cs2_data.json.</td></tr>`;
  }
}
main();
