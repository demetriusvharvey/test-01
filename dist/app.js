(function () {
  'use strict';
  const games = window.LINE_LAB_GAMES;
  const moneylineProbability = o => o < 0 ? -o / (-o + 100) : 100 / (o + 100);
  const validOdds = n => Number.isFinite(n) && Number.isInteger(n) && Math.abs(n) >= 100;
  const signed = n => n > 0 ? '+' + n : '−' + Math.abs(n);
  const percent = n => (n * 100).toFixed(1) + '%';
  const money = n => (n < 0 ? '−' : '') + '$' + Math.abs(n).toFixed(2);
  const gamesEl = document.getElementById('games');
  function renderGames(filter) {
    gamesEl.replaceChildren();
    games.filter(g => filter === 'all' || g.league === filter).forEach(g => {
      const item = document.createElement('article'); item.className = 'game';
      const links = g.sources.map(([label,url]) => `<a href="${url}" target="_blank" rel="noopener noreferrer">${label} ↗</a>`).join(' &nbsp; ');
      item.innerHTML = `<div><div class="game-time">${g.league} &nbsp; / &nbsp; ${g.when}</div><div class="teams">${g.selected} ML <small>${g.homeAway}</small></div></div><div class="game-stat"><span class="tiny-label">FANDUEL SNAPSHOT</span><strong>${signed(g.price)}</strong><small>Other side ${signed(g.other)}</small></div><div class="game-stat"><span class="tiny-label">BREAK-EVEN / FORECAST</span><strong>${percent(moneylineProbability(g.price))} <span style="color:#c3cec0">/</span> ${g.models}</strong><small>${g.modelNote}</small></div><div class="game-action"><span class="tag ${g.tone}">${g.verdict}</span><button class="details-button" aria-expanded="false" aria-controls="details-${g.id}">See game notes ＋</button></div><div id="details-${g.id}" class="game-details" hidden><div><h4>AVAILABILITY</h4><p>${g.availability}</p></div><div><h4>SCHEDULE</h4><p>${g.rest}</p></div><div><h4>REFEREES</h4><p>${g.officials}</p></div><div style="grid-column:1/-1"><h4>SOURCES</h4><p>${links}</p></div></div>`;
      const button = item.querySelector('button'); const details = item.querySelector('.game-details');
      button.addEventListener('click', () => { const expanded = button.getAttribute('aria-expanded') === 'true'; button.setAttribute('aria-expanded', String(!expanded)); details.hidden = expanded; button.textContent = expanded ? 'See game notes ＋' : 'Hide game notes −'; });
      gamesEl.append(item);
    });
  }
  document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('.filter').forEach(b => { b.classList.toggle('active', b === button); b.setAttribute('aria-pressed', String(b === button)); });
    renderGames(button.dataset.filter);
  }));
  renderGames('all');
  const f = document.getElementById('calc-form');
  const ids = ['break-even','no-vig','profit','expected'];
  function calculate() {
    const oddsRaw = document.getElementById('odds').value.trim();
    const oppRaw = document.getElementById('opponent').value.trim();
    const pRaw = document.getElementById('probability').value.trim();
    const stakeRaw = document.getElementById('stake').value.trim();
    const odds = Number(oddsRaw), opp = Number(oppRaw), probability = Number(pRaw), stake = Number(stakeRaw);
    const error = document.getElementById('calc-error');
    let message = '';
    if (!oddsRaw || !validOdds(odds)) message = 'Use a whole American moneyline at or above +100, or at or below −100.';
    else if (oppRaw && !validOdds(opp)) message = 'The opposing moneyline must be a whole number at or above +100, or at or below −100.';
    else if (!pRaw || !Number.isFinite(probability) || probability < 0 || probability > 100) message = 'Enter an assumed chance from 0 to 100%.';
    else if (!stakeRaw || !Number.isFinite(stake) || stake < 0) message = 'Enter a stake of $0 or more.';
    error.textContent = message;
    if (message) { ids.forEach(id => document.getElementById(id).textContent = '—'); return; }
    const p = moneylineProbability(odds), payout = stake * (odds < 0 ? 100 / -odds : odds / 100);
    const noVig = oppRaw ? p / (p + moneylineProbability(opp)) : null;
    document.getElementById('break-even').textContent = percent(p);
    document.getElementById('no-vig').textContent = noVig === null ? '—' : percent(noVig);
    document.getElementById('profit').textContent = money(payout);
    document.getElementById('expected').textContent = money((probability / 100) * payout - (1 - probability / 100) * stake);
  }
  f.addEventListener('input', calculate); f.addEventListener('submit', e => e.preventDefault()); calculate();
  // Exposed for small, behavior-focused tests; not a predictive model.
  window.LineLabMath = {moneylineProbability, validOdds};
}());
