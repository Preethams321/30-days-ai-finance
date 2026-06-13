// ===================== STATE =====================
const state = {
  age: 28,
  income: 80000,
  expenses: 50000,
  savings: 500000,
  annualReturn: 0.10,
  inflation: 0.06,
  swr: 0.04,
  fieldsCompleted: new Set(['age'])
};

const results = {};

// ===================== PAGE ROUTING =====================
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
}

// ===================== FORMATTING =====================
function formatINR(n) {
  if (isNaN(n) || n === null || n === undefined) return '—';
  n = Math.round(n);
  if (n < 0) return '-' + formatINR(-n);
  const s = n.toString();
  if (s.length <= 3) return '₹' + s;
  const last3 = s.slice(-3);
  const rest = s.slice(0, -3);
  const grouped = rest.replace(/\B(?=(\d{2})+(?!\d))/g, ',');
  return '₹' + grouped + ',' + last3;
}

function formatCrLakh(n) {
  if (isNaN(n) || n == null) return '—';
  if (n >= 10000000) return '₹' + (n / 10000000).toFixed(2) + ' Cr';
  if (n >= 100000) return '₹' + (n / 100000).toFixed(1) + 'L';
  return formatINR(n);
}

function formatYears(y) {
  if (y <= 0) return 'Already there!';
  const yrs = Math.floor(y);
  const months = Math.round((y - yrs) * 12);
  if (months === 0) return yrs + ' years';
  if (yrs === 0) return months + ' months';
  return yrs + ' years, ' + months + ' months';
}

function dateFromYears(yearsFromNow) {
  const now = new Date();
  const target = new Date(now);
  const months = Math.round(yearsFromNow * 12);
  target.setMonth(target.getMonth() + months);
  const months_list = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  return months_list[target.getMonth()] + ' ' + target.getFullYear();
}

function dateObjFromYears(yearsFromNow) {
  const now = new Date();
  const target = new Date(now);
  const months = Math.round(yearsFromNow * 12);
  target.setMonth(target.getMonth() + months);
  return target;
}

// ===================== FIRE MATH =====================
function yearsToFIRE(currentSavings, monthlyContribution, annualReturn, freedomNumber) {
  if (currentSavings >= freedomNumber) return 0;
  if (monthlyContribution <= 0 && currentSavings <= 0) return 600;
  let corpus = currentSavings;
  const monthlyRate = annualReturn / 12;
  let months = 0;
  while (corpus < freedomNumber && months < 600) {
    corpus = corpus * (1 + monthlyRate) + monthlyContribution;
    months++;
  }
  return months / 12;
}

function calcFreedomNumber(annualExpenses, swr) {
  return annualExpenses / swr;
}

function calcEscapeScore(savingsRate, fireAge, progressPct) {
  const srScore = Math.min(savingsRate / 0.5, 1) * 40;
  const ageScore = Math.max(0, (60 - fireAge) / 35) * 30;
  const prScore = Math.min(progressPct / 100, 1) * 30;
  return { total: Math.round(srScore + ageScore + prScore), sr: Math.round(srScore), age: Math.round(ageScore), pr: Math.round(prScore) };
}

function corpusAtYear(currentSavings, monthlyContribution, annualReturn, years) {
  let corpus = currentSavings;
  const monthlyRate = annualReturn / 12;
  const months = Math.round(years * 12);
  for (let i = 0; i < months; i++) {
    corpus = corpus * (1 + monthlyRate) + monthlyContribution;
  }
  return corpus;
}

function realValue(nominalValue, inflationRate, years) {
  return nominalValue / Math.pow(1 + inflationRate, years);
}

// ===================== RANGE SLIDER FILL =====================
function updateSliderFill(el) {
  const min = parseFloat(el.min);
  const max = parseFloat(el.max);
  const val = parseFloat(el.value);
  const pct = ((val - min) / (max - min)) * 100;
  el.style.setProperty('--pct', pct + '%');
}

// ===================== INPUT PAGE =====================
function initInputPage() {
  document.querySelectorAll('input[type="range"]').forEach(el => updateSliderFill(el));
  updateAge(28);
  updateIncome(80000);
  updateExpenses(50000);
  updateSavings(500000);
  updateReturn(10);
  updateInflation(6);
  updateSWR(4);
  updateProgress();
}

function activateField(id) {
  const f = document.getElementById(id);
  if (f) { f.classList.add('active'); }
}

function markCompleted(fieldId, checkId) {
  const f = document.getElementById(fieldId);
  if (f) { f.classList.remove('active'); f.classList.add('completed'); }
  const c = document.getElementById(checkId);
  if (c) c.style.display = 'inline';
}

function updateProgress() {
  const total = 7;
  const done = state.fieldsCompleted.size;
  const pct = Math.round((done / total) * 100);
  const fill = document.getElementById('inputProgress');
  const label = document.getElementById('inputProgressLabel');
  if (fill) fill.style.width = pct + '%';
  if (label) label.textContent = pct + '% complete';
}

function updateAge(v) {
  state.age = parseInt(v);
  const el = document.getElementById('ageVal');
  if (el) el.textContent = v;
  updateSliderFill(document.getElementById('ageSlider'));
  state.fieldsCompleted.add('age');
  markCompleted('fieldAge', 'checkAge');
  updateProgress();
  // Activate next
  activateField('fieldIncome');
}

function updateIncome(v) {
  state.income = parseFloat(v) || 0;
  if (state.income > 0) {
    state.fieldsCompleted.add('income');
    markCompleted('fieldIncome', 'checkIncome');
    const g = document.getElementById('ghostIncome');
    if (g) g.textContent = "Good start. Let's see how fast you can escape.";
    activateField('fieldExpenses');
    updateProgress();
  }
}

function updateExpenses(v) {
  state.expenses = parseFloat(v) || 0;
  if (state.expenses >= 0 && state.income > 0) {
    state.fieldsCompleted.add('expenses');
    markCompleted('fieldExpenses', 'checkExpenses');
    activateField('fieldSavings');
    updateProgress();
  }
  const sr = state.income > 0 ? ((state.income - state.expenses) / state.income) : 0;
  const srPct = Math.round(sr * 100);
  const wrap = document.getElementById('savingsRateBadgeWrap');
  const ghost = document.getElementById('ghostExpenses');
  if (wrap) {
    let cls = 'low', label = 'Tight. But fixable.';
    if (srPct >= 40) { cls = 'high'; label = "You're built different."; }
    else if (srPct >= 20) { cls = 'mid'; label = 'Solid foundation.'; }
    wrap.innerHTML = `<span class="savings-rate-badge ${cls}">Savings Rate: ${srPct}%</span>`;
  }
  if (ghost) {
    let msg = '';
    if (srPct < 20) msg = `Your savings rate is ${srPct}%. Tight. But fixable.`;
    else if (srPct < 40) msg = `Your savings rate is ${srPct}%. Solid foundation.`;
    else msg = `Your savings rate is ${srPct}%. You're built different.`;
    ghost.textContent = msg;
  }
}

function updateSavings(v) {
  state.savings = parseFloat(v) || 0;
  if (state.savings >= 0) {
    state.fieldsCompleted.add('savings');
    markCompleted('fieldSavings', 'checkSavings');
    activateField('fieldReturn');
    updateProgress();
  }
  const ghost = document.getElementById('ghostSavings');
  if (ghost && state.savings > 0) ghost.textContent = `${formatCrLakh(state.savings)} already saved. That's your head start.`;
}

function updateReturn(v) {
  state.annualReturn = parseFloat(v) / 100;
  const el = document.getElementById('returnVal');
  if (el) el.textContent = parseFloat(v).toFixed(1);
  updateSliderFill(document.getElementById('returnSlider'));
  state.fieldsCompleted.add('return');
  markCompleted('fieldReturn', 'checkReturn');
  activateField('fieldInflation');
  updateProgress();
}

function updateInflation(v) {
  state.inflation = parseFloat(v) / 100;
  const el = document.getElementById('inflationVal');
  if (el) el.textContent = parseFloat(v).toFixed(1);
  updateSliderFill(document.getElementById('inflationSlider'));
  state.fieldsCompleted.add('inflation');
  markCompleted('fieldInflation', 'checkInflation');
  activateField('fieldSWR');
  updateProgress();
}

function updateSWR(v) {
  state.swr = parseFloat(v) / 100;
  const el = document.getElementById('swrVal');
  if (el) el.textContent = parseFloat(v).toFixed(1);
  updateSliderFill(document.getElementById('swrSlider'));
  state.fieldsCompleted.add('swr');
  markCompleted('fieldSWR', 'checkSWR');
  updateProgress();
}

// ===================== MAIN CALCULATION =====================
function calculateFIRE() {
  const monthlySavings = state.income - state.expenses;
  const annualExpenses = state.expenses * 12;
  const fn = calcFreedomNumber(annualExpenses, state.swr);
  const yrs = yearsToFIRE(state.savings, monthlySavings, state.annualReturn, fn);
  const savingsRate = state.income > 0 ? (monthlySavings / state.income) : 0;
  const progressPct = Math.min((state.savings / fn) * 100, 100);
  const fireAge = state.age + yrs;
  const score = calcEscapeScore(savingsRate, fireAge, progressPct);

  results.monthlySavings = monthlySavings;
  results.annualSavings = monthlySavings * 12;
  results.freedomNumber = fn;
  results.yearsToFire = yrs;
  results.fireDate = dateFromYears(yrs);
  results.fireDateObj = dateObjFromYears(yrs);
  results.fireAge = fireAge;
  results.progressPct = progressPct;
  results.savingsRate = savingsRate;
  results.score = score;
  results.corpusAtFire = corpusAtYear(state.savings, monthlySavings, state.annualReturn, yrs);
  results.realCorpusAtFire = realValue(results.corpusAtFire, state.inflation, yrs);
  results.realAnnualIncome = results.corpusAtFire * state.swr;

  showPage('resultsPage');
  renderResults();
}

function renderResults() {
  const r = results;

  // Handle already-FIRE state
  if (r.yearsToFire <= 0) {
    document.getElementById('congratsBlock').style.display = 'block';
    document.getElementById('normalResultsBlock').style.display = 'none';
    return;
  }
  document.getElementById('congratsBlock').style.display = 'none';
  document.getElementById('normalResultsBlock').style.display = 'block';

  // Section 1: Verdict
  animateText('fireDate', r.fireDate);
  animateText('yearsToFire', formatYears(r.yearsToFire));
  animateText('fireAge', Math.round(r.fireAge) + ' years old');
  animateText('freedomNumber', formatCrLakh(r.freedomNumber));
  document.getElementById('verdictFNInline').textContent = formatCrLakh(r.freedomNumber);

  setTimeout(() => {
    const fill = document.getElementById('corpusProgressFill');
    if (fill) fill.style.width = Math.min(r.progressPct, 100) + '%';
    document.getElementById('corpusProgressPct').textContent = r.progressPct.toFixed(1) + '%';
  }, 400);

  // Fire badge
  const fb = document.getElementById('fireBadge');
  if (fb) {
    let badgeClass = 'standard', badgeLabel = '🎯 Standard Retirement';
    if (r.freedomNumber < 5000000) { badgeClass = 'lean'; badgeLabel = '🪶 Lean FIRE'; }
    else if (r.freedomNumber > 20000000) { badgeClass = 'fat'; badgeLabel = '👑 Fat FIRE'; }
    else if (r.fireAge < 45) { badgeClass = 'fat'; badgeLabel = '⚡ Early Retirement'; }
    fb.innerHTML = `<span class="fire-mode-badge ${badgeClass}">${badgeLabel}</span>`;
  }

  // Section 2: Dashboard
  animateText('mMonthlySavings', formatINR(r.monthlySavings));
  document.getElementById('mSavingsRate').textContent = 'Savings Rate: ' + Math.round(r.savingsRate * 100) + '%';
  animateText('mAnnualSavings', formatINR(r.annualSavings));
  animateText('mCorpusAtFire', formatCrLakh(r.corpusAtFire));
  document.getElementById('mCorpusInflAdj').textContent = 'Real value: ' + formatCrLakh(r.realCorpusAtFire);
  animateText('mRealAnnualIncome', formatINR(r.realAnnualIncome));

  // Section 3: Score
  renderScoreGauge(r.score.total);
  animateText('scoreNumber', r.score.total);
  document.getElementById('scoreSR').textContent = r.score.sr + '/40';
  document.getElementById('scoreFA').textContent = r.score.age + '/30';
  document.getElementById('scorePR').textContent = r.score.pr + '/30';
  const scoreInfo = getScoreInfo(r.score.total);
  document.getElementById('scoreTitle').textContent = scoreInfo.label;
  const ss = document.getElementById('scoreStatus');
  ss.textContent = scoreInfo.status;
  ss.style.background = scoreInfo.bg;
  ss.style.color = scoreInfo.color;

  // Section 4: Timeline
  renderTimeline();

  // Section 5: Chart
  setTimeout(() => renderCorpusChart(), 300);

  // Levers
  resetLevers();

  // FIRE modes
  setFIREMode('lean', document.querySelector('.firemode-tab.active'));
  document.querySelectorAll('.firemode-tab').forEach((t, i) => {
    if (i === 0) { t.classList.add('active'); } else { t.classList.remove('active'); }
  });
  setFIREMode('lean', document.querySelector('.firemode-tab'));

  // Badges
  renderBadges();

  // Regret calc
  renderRegret();

  // Compare
  renderCompare();
}

function getScoreInfo(score) {
  if (score <= 25) return { label: 'Still Trapped', status: 'Needs Work', bg: 'rgba(224,92,108,0.15)', color: '#e05c6c' };
  if (score <= 50) return { label: 'Planning the Escape', status: 'Making Progress', bg: 'rgba(224,160,74,0.15)', color: '#e0a04a' };
  if (score <= 75) return { label: 'On the Run', status: 'On Track', bg: 'rgba(201,169,110,0.15)', color: '#c9a96e' };
  if (score <= 90) return { label: 'Almost Free', status: 'Nearly There', bg: 'rgba(74,184,122,0.15)', color: '#4ab87a' };
  return { label: 'FIRE Achieved', status: 'Financially Free', bg: 'rgba(74,184,122,0.2)', color: '#4ab87a' };
}

// ===================== SCORE GAUGE =====================
function renderScoreGauge(score) {
  const canvas = document.getElementById('scoreGauge');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const cx = 70, cy = 70, r = 55;
  ctx.clearRect(0, 0, 140, 140);

  // Background arc
  ctx.beginPath();
  ctx.arc(cx, cy, r, Math.PI * 0.75, Math.PI * 2.25);
  ctx.strokeStyle = '#1e1e2a';
  ctx.lineWidth = 10;
  ctx.lineCap = 'round';
  ctx.stroke();

  // Score arc
  const startAngle = Math.PI * 0.75;
  const endAngle = startAngle + (score / 100) * (Math.PI * 1.5);
  const scoreColor = score <= 25 ? '#e05c6c' : score <= 50 ? '#e0a04a' : score <= 75 ? '#c9a96e' : '#4ab87a';

  ctx.beginPath();
  ctx.arc(cx, cy, r, startAngle, endAngle);
  ctx.strokeStyle = scoreColor;
  ctx.lineWidth = 10;
  ctx.lineCap = 'round';
  ctx.stroke();
}

// ===================== TIMELINE =====================
function renderTimeline() {
  const track = document.getElementById('timelineTrack');
  if (!track) return;
  track.innerHTML = '';

  const r = results;
  const monthlySavings = state.income - state.expenses;
  const milestones = [];

  // Today
  milestones.push({ icon: '🏁', label: 'Today', amount: formatCrLakh(state.savings), sub: 'Starting point', years: 0, isNow: true });

  // First ₹10L
  if (state.savings < 1000000) {
    const y = yearsToFIRE(state.savings, monthlySavings, state.annualReturn, 1000000);
    if (y > 0 && y < r.yearsToFire) milestones.push({ icon: '💰', label: '₹10L', amount: '₹10 Lakhs', sub: 'in ' + formatYears(y), years: y });
  }

  // First ₹50L
  if (state.savings < 5000000) {
    const y = yearsToFIRE(state.savings, monthlySavings, state.annualReturn, 5000000);
    if (y > 0 && y < r.yearsToFire) milestones.push({ icon: '🌟', label: '₹50L', amount: '₹50 Lakhs', sub: 'in ' + formatYears(y), years: y });
  }

  // First ₹1 Crore
  if (state.savings < 10000000) {
    const y = yearsToFIRE(state.savings, monthlySavings, state.annualReturn, 10000000);
    if (y > 0 && y < r.yearsToFire) milestones.push({ icon: '🏆', label: '₹1 Cr', amount: '₹1 Crore', sub: 'in ' + formatYears(y), years: y });
  }

  // FIRE date
  milestones.push({ icon: '🔥', label: 'FIRE!', amount: formatCrLakh(r.freedomNumber), sub: r.fireDate, years: r.yearsToFire, isFire: true });

  milestones.forEach((m, i) => {
    if (i > 0) {
      const conn = document.createElement('div');
      conn.className = 'timeline-connector';
      track.appendChild(conn);
    }
    const item = document.createElement('div');
    item.className = 'timeline-item';
    item.innerHTML = `
      <div class="timeline-node ${m.isNow ? 'now' : ''} ${m.isFire ? 'fire' : ''}">${m.icon}</div>
      <div class="timeline-date">${m.label}</div>
      <div class="timeline-amount">${m.amount}</div>
      <div class="timeline-sub">${m.sub}</div>
    `;
    track.appendChild(item);
    setTimeout(() => item.classList.add('visible'), i * 200 + 400);
  });
}

// ===================== CORPUS CHART =====================
function renderCorpusChart() {
  const canvas = document.getElementById('corpusChart');
  if (!canvas) return;
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.parentElement.offsetWidth - 0;
  const H = 220;
  canvas.width = W * dpr;
  canvas.height = H * dpr;
  canvas.style.width = W + 'px';
  canvas.style.height = H + 'px';
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  const r = results;
  const monthlySavings = state.income - state.expenses;
  const totalYears = Math.min(Math.ceil(r.yearsToFire) + 2, 52);
  const years = Array.from({ length: totalYears + 1 }, (_, i) => i);

  const nominal = years.map(y => corpusAtYear(state.savings, monthlySavings, state.annualReturn, y));
  const real = years.map(y => realValue(nominal[y], state.inflation, y));
  const fn = r.freedomNumber;

  const maxVal = Math.max(...nominal, fn) * 1.05;

  const pad = { top: 20, right: 20, bottom: 40, left: 70 };
  const chartW = W - pad.left - pad.right;
  const chartH = H - pad.top - pad.bottom;

  const xScale = x => pad.left + (x / totalYears) * chartW;
  const yScale = y => pad.top + chartH - (y / maxVal) * chartH;

  ctx.clearRect(0, 0, W, H);

  // Grid lines
  ctx.strokeStyle = '#1e1e2a';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + (i / 4) * chartH;
    ctx.beginPath();
    ctx.moveTo(pad.left, y);
    ctx.lineTo(pad.left + chartW, y);
    ctx.stroke();
    const val = maxVal * (1 - i / 4);
    ctx.fillStyle = '#5a5870';
    ctx.font = '10px DM Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillText(formatCrLakh(val), pad.left - 6, y + 4);
  }

  // X axis labels
  ctx.fillStyle = '#5a5870';
  ctx.font = '10px DM Mono, monospace';
  ctx.textAlign = 'center';
  const step = Math.max(1, Math.floor(totalYears / 6));
  for (let y = 0; y <= totalYears; y += step) {
    ctx.fillText('Y' + y, xScale(y), H - 10);
  }

  // Freedom number line
  ctx.beginPath();
  ctx.moveTo(pad.left, yScale(fn));
  ctx.lineTo(pad.left + chartW, yScale(fn));
  ctx.strokeStyle = 'rgba(74,184,122,0.4)';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([6, 4]);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = '#4ab87a';
  ctx.font = '9px DM Mono, monospace';
  ctx.textAlign = 'left';
  ctx.fillText('Freedom Number', pad.left + 4, yScale(fn) - 5);

  // Real value line (dimmer)
  ctx.beginPath();
  years.forEach((y, i) => {
    const x = xScale(y);
    const yy = yScale(real[i]);
    if (i === 0) ctx.moveTo(x, yy);
    else ctx.lineTo(x, yy);
  });
  ctx.strokeStyle = 'rgba(138,111,64,0.45)';
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // Nominal line (gold)
  ctx.beginPath();
  years.forEach((y, i) => {
    const x = xScale(y);
    const yy = yScale(nominal[i]);
    if (i === 0) ctx.moveTo(x, yy);
    else ctx.lineTo(x, yy);
  });
  ctx.strokeStyle = '#c9a96e';
  ctx.lineWidth = 2.5;
  ctx.stroke();

  // Fill under nominal
  ctx.beginPath();
  years.forEach((y, i) => {
    const x = xScale(y);
    const yy = yScale(nominal[i]);
    if (i === 0) ctx.moveTo(x, yy);
    else ctx.lineTo(x, yy);
  });
  ctx.lineTo(xScale(totalYears), yScale(0));
  ctx.lineTo(pad.left, yScale(0));
  ctx.closePath();
  const grad = ctx.createLinearGradient(0, pad.top, 0, pad.top + chartH);
  grad.addColorStop(0, 'rgba(201,169,110,0.15)');
  grad.addColorStop(1, 'rgba(201,169,110,0)');
  ctx.fillStyle = grad;
  ctx.fill();

  // Crossover point
  const crossYear = r.yearsToFire;
  if (crossYear <= totalYears) {
    const cx = xScale(crossYear);
    const cy = yScale(fn);
    ctx.beginPath();
    ctx.arc(cx, cy, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#4ab87a';
    ctx.fill();
    ctx.strokeStyle = '#09090e';
    ctx.lineWidth = 2;
    ctx.stroke();
  }
}

// ===================== LEVERS =====================
function resetLevers() {
  ['lever1','lever2','lever3','lever4'].forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.value = 0; updateSliderFill(el); }
  });
  document.getElementById('lever1Val').textContent = '+₹0';
  document.getElementById('lever2Val').textContent = '+0%';
  document.getElementById('lever3Val').textContent = '-0%';
  document.getElementById('lever4Val').textContent = '+0%';
  document.getElementById('leverFireDate').textContent = results.fireDate || '—';
  document.getElementById('leverDiff').textContent = '';
  document.getElementById('leverDiff').className = 'lever-impact neutral';
  ['lever1Impact','lever2Impact','lever3Impact','lever4Impact'].forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.textContent = 'Move the slider to see impact'; el.className = 'lever-impact neutral'; }
  });
}

function updateLevers() {
  const l1 = parseFloat(document.getElementById('lever1').value);
  const l2 = parseFloat(document.getElementById('lever2').value) / 100;
  const l3 = parseFloat(document.getElementById('lever3').value) / 100;
  const l4 = parseFloat(document.getElementById('lever4').value) / 100;

  document.getElementById('lever1Val').textContent = '+₹' + l1.toLocaleString('en-IN');
  document.getElementById('lever2Val').textContent = '+' + (l2 * 100).toFixed(0) + '%';
  document.getElementById('lever3Val').textContent = '-' + (l3 * 100).toFixed(0) + '%';
  document.getElementById('lever4Val').textContent = (l4 >= 0 ? '+' : '') + (l4 * 100).toFixed(1) + '%';

  ['lever1','lever2','lever3','lever4'].forEach(id => updateSliderFill(document.getElementById(id)));

  const newIncome = state.income * (1 + l2);
  const newExpenses = state.expenses * (1 - l3);
  const newMonthlySavings = (newIncome - newExpenses) + l1;
  const newReturn = state.annualReturn + l4;
  const fn = results.freedomNumber;

  const newYears = yearsToFIRE(state.savings, newMonthlySavings, newReturn, fn);
  const newDate = dateFromYears(newYears);
  const diff = results.yearsToFire - newYears;
  const diffMonths = Math.round(Math.abs(diff) * 12);

  document.getElementById('leverFireDate').textContent = newDate;

  const diffEl = document.getElementById('leverDiff');
  if (Math.abs(diff) < 0.08) {
    diffEl.textContent = 'No change from current plan';
    diffEl.className = 'lever-impact neutral';
  } else if (diff > 0) {
    diffEl.textContent = `⚡ You just moved your FIRE date ${diffMonths} months earlier!`;
    diffEl.className = 'lever-impact positive';
  } else {
    diffEl.textContent = `⚠ This moves your FIRE date ${diffMonths} months later.`;
    diffEl.className = 'lever-impact negative';
  }

  // Individual lever impacts
  function impactText(origYears, newY, impactId) {
    const d = origYears - newY;
    const m = Math.round(Math.abs(d) * 12);
    const el = document.getElementById(impactId);
    if (!el) return;
    if (m < 1) { el.textContent = '—'; el.className = 'lever-impact neutral'; return; }
    if (d > 0) { el.textContent = `⚡ ${m} months earlier`; el.className = 'lever-impact positive'; }
    else { el.textContent = `▼ ${m} months later`; el.className = 'lever-impact negative'; }
  }

  const base = results.yearsToFire;
  const fn2 = results.freedomNumber;
  const ms0 = state.income - state.expenses;

  impactText(base, yearsToFIRE(state.savings, ms0 + l1, state.annualReturn, fn2), 'lever1Impact');
  impactText(base, yearsToFIRE(state.savings, state.income*(1+l2) - state.expenses, state.annualReturn, fn2), 'lever2Impact');
  const newExp = state.expenses*(1-l3);
  const newFN3 = calcFreedomNumber(newExp*12, state.swr);
  impactText(base, yearsToFIRE(state.savings, state.income - newExp, state.annualReturn, newFN3), 'lever3Impact');
  impactText(base, yearsToFIRE(state.savings, ms0, newReturn, fn2), 'lever4Impact');
}

// ===================== FIRE MODES =====================
function setFIREMode(mode, btn) {
  document.querySelectorAll('.firemode-tab').forEach(t => t.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const ms = state.income - state.expenses;
  const annExpBase = state.expenses * 12;

  let expMultiplier = 1, msMultiplier = 1, label = '', note = '';
  switch (mode) {
    case 'lean':
      expMultiplier = 0.7; msMultiplier = 1.3;
      label = 'Lean FIRE'; note = 'Expenses cut 30%. Frugal, efficient lifestyle.';
      break;
    case 'regular':
      expMultiplier = 1; msMultiplier = 1;
      label = 'Regular FIRE'; note = 'Current expenses maintained.';
      break;
    case 'fat':
      expMultiplier = 1.5; msMultiplier = 0.5;
      label = 'Fat FIRE'; note = 'Expenses up 50%. Luxury retirement.';
      break;
    case 'barista':
      expMultiplier = 0.6; msMultiplier = 1.0;
      label = 'Barista FIRE'; note = 'Corpus covers 60% of expenses. Part-time income covers the rest.';
      break;
  }

  // Barista: FN only needs to cover 60% of full expenses. You still spend same total.
  // Monthly savings = full income - full expenses (same as regular, part-time comes later)
  const modeExpenses = mode === 'barista' ? state.expenses * 0.6 : state.expenses * expMultiplier;
  const modeAnnExp = modeExpenses * 12;
  const modeFN = calcFreedomNumber(modeAnnExp, state.swr);
  const modeMS = state.income - state.expenses;
  const modeYears = yearsToFIRE(state.savings, modeMS, state.annualReturn, modeFN);
  const modeDate = dateFromYears(modeYears);
  const modeAge = state.age + modeYears;
  const diff = results.yearsToFire - modeYears;
  const diffMonths = Math.round(Math.abs(diff) * 12);

  const res = document.getElementById('firemodeResults');
  if (res) {
    res.innerHTML = `
      <div class="firemode-result-item">
        <div class="firemode-result-label">FIRE Date</div>
        <div class="firemode-result-value" style="color:var(--gold)">${modeDate}</div>
      </div>
      <div class="firemode-result-item">
        <div class="firemode-result-label">Years to FIRE</div>
        <div class="firemode-result-value">${formatYears(modeYears)}</div>
      </div>
      <div class="firemode-result-item">
        <div class="firemode-result-label">FIRE Age</div>
        <div class="firemode-result-value">${Math.round(modeAge)}</div>
      </div>
      <div class="firemode-result-item">
        <div class="firemode-result-label">Freedom Number</div>
        <div class="firemode-result-value">${formatCrLakh(modeFN)}</div>
      </div>
      <div class="firemode-result-item">
        <div class="firemode-result-label">vs Regular FIRE</div>
        <div class="firemode-result-value" style="color:${diff >= 0 ? 'var(--green)' : 'var(--red)'}">
          ${diff >= 0 ? '⚡ ' + diffMonths + ' mo earlier' : '▼ ' + diffMonths + ' mo later'}
        </div>
      </div>
      <div class="firemode-result-item" style="grid-column:1/-1">
        <div class="firemode-result-label">Mode Note</div>
        <div style="font-size:0.75rem;color:var(--text-muted);margin-top:4px">${note}</div>
      </div>
    `;
  }
}

// ===================== BADGES =====================
function renderBadges() {
  const allBadges = [
    { id: 'complete', icon: '📋', name: 'Planner', xp: 100, desc: 'Completed all input fields', condition: true },
    { id: 'saver30', icon: '💪', name: 'High Saver', xp: 50, desc: 'Savings rate above 30%', condition: results.savingsRate >= 0.3 },
    { id: 'saver50', icon: '⚔️', name: 'FIRE Warrior', xp: 100, desc: 'Savings rate above 50%', condition: results.savingsRate >= 0.5 },
    { id: 'early45', icon: '🚀', name: 'Early Escaper', xp: 75, desc: 'FIRE age below 45', condition: results.fireAge < 45 },
    { id: 'headstart', icon: '🏆', name: 'Head Start', xp: 50, desc: 'Already have >₹10L saved', condition: state.savings >= 1000000 },
    { id: 'halfcr', icon: '💎', name: 'Half Crore Club', xp: 75, desc: 'Current savings above ₹50L', condition: state.savings >= 5000000 },
    { id: 'crclub', icon: '👑', name: 'Crore Club', xp: 150, desc: 'Current savings above ₹1 Crore', condition: state.savings >= 10000000 },
  ];

  const grid = document.getElementById('badgesGrid');
  if (!grid) return;
  grid.innerHTML = '';
  let totalXP = 0;

  allBadges.forEach((b, i) => {
    const earned = b.condition;
    if (earned) totalXP += b.xp;
    const div = document.createElement('div');
    div.className = 'badge ' + (earned ? '' : 'locked');
    div.innerHTML = `
      <span class="badge-icon">${b.icon}</span>
      <div class="badge-info">
        <div class="badge-name">${b.name}</div>
        <div class="badge-xp">+${b.xp} XP · ${b.desc}</div>
      </div>
    `;
    grid.appendChild(div);
    if (earned) setTimeout(() => div.classList.add('earned'), i * 150 + 300);
  });

  const xpEl = document.getElementById('totalXP');
  if (xpEl) xpEl.textContent = 'Total XP: ' + totalXP + ' pts';
}

// ===================== REGRET CALC =====================
function renderRegret() {
  const monthlySavings = state.income - state.expenses;
  const fn = results.freedomNumber;

  const earlyAge = state.age - 5;
  const yearsExtra = 5;
  const earlyStartSavings = corpusAtYear(0, monthlySavings, state.annualReturn, yearsExtra);
  const earlyTotalSavings = state.savings + earlyStartSavings;
  const earlyYears = yearsToFIRE(earlyTotalSavings, monthlySavings, state.annualReturn, fn);
  const yearsDiff = results.yearsToFire - earlyYears;

  // If you wait 5 more years: you lose 5 years of compounding on current savings
  // Model: you'd start with current savings but lose 5 years of investment growth
  // Equivalently, from that future date you'd need yearsToFIRE from a smaller base
  const lostGrowth = corpusAtYear(state.savings, 0, state.annualReturn, 5) - state.savings; // pure growth lost
  const lateSavingsBase = Math.max(0, state.savings - lostGrowth);
  const lateYears = yearsToFIRE(lateSavingsBase, monthlySavings, state.annualReturn, fn) + 5;
  const lateDiff = lateYears - results.yearsToFire;

  const el = document.getElementById('regretNumbers');
  if (!el) return;
  el.innerHTML = `
    <div class="regret-item">
      <div class="regret-item-label">If started at age ${earlyAge}</div>
      <div class="regret-item-value gain">FIRE ${formatYears(Math.max(0, yearsDiff))} earlier</div>
      <p style="font-size:0.72rem;color:var(--text-muted);margin-top:6px">Corpus head start: ${formatCrLakh(earlyStartSavings)} extra</p>
    </div>
    <div class="regret-item">
      <div class="regret-item-label">If you wait 5 more years</div>
      <div class="regret-item-value loss">FIRE ${formatYears(Math.max(0, lateDiff))} later</div>
      <p style="font-size:0.72rem;color:var(--text-muted);margin-top:6px">Cost of delay: ${formatCrLakh(corpusAtYear(0, monthlySavings, state.annualReturn, 5))} less to start with</p>
    </div>
    <div class="regret-item">
      <div class="regret-item-label">Every year you delay costs</div>
      <div class="regret-item-value loss">${formatYears(Math.abs(yearsDiff / 5))} of FIRE time</div>
      <p style="font-size:0.72rem;color:var(--text-muted);margin-top:6px">Average per year of delay at your current savings rate</p>
    </div>
  `;
}

// ===================== COMPARE PATHS =====================
function renderCompare() {
  const el = document.getElementById('compareGrid');
  if (!el) return;

  // Best case: all levers maxed
  const bestExtraSavings = 25000;
  const bestRaiseIncome = state.income * 1.20;
  const bestExpCut = state.expenses * 0.80;
  const bestReturn = state.annualReturn + 0.015;
  const bestMS = (bestRaiseIncome - bestExpCut) + bestExtraSavings;
  const bestFN = calcFreedomNumber(bestExpCut * 12, state.swr);
  const bestYears = yearsToFIRE(state.savings, bestMS, bestReturn, bestFN);
  const bestDate = dateFromYears(bestYears);
  const bestCorpus = corpusAtYear(state.savings, bestMS, bestReturn, bestYears);
  const diff = results.yearsToFire - bestYears;

  el.innerHTML = `
    <div class="compare-col">
      <div class="compare-col-title current">📍 Current Plan</div>
      <div class="compare-row"><span class="compare-row-label">FIRE Date</span><span class="compare-row-val">${results.fireDate}</span></div>
      <div class="compare-row"><span class="compare-row-label">Years to FIRE</span><span class="compare-row-val">${formatYears(results.yearsToFire)}</span></div>
      <div class="compare-row"><span class="compare-row-label">FIRE Age</span><span class="compare-row-val">${Math.round(results.fireAge)}</span></div>
      <div class="compare-row"><span class="compare-row-label">Freedom Number</span><span class="compare-row-val">${formatCrLakh(results.freedomNumber)}</span></div>
      <div class="compare-row"><span class="compare-row-label">Corpus at FIRE</span><span class="compare-row-val">${formatCrLakh(results.corpusAtFire)}</span></div>
    </div>
    <div class="compare-col">
      <div class="compare-col-title best">⚡ Best Case (All Levers)</div>
      <div class="compare-row"><span class="compare-row-label">FIRE Date</span><span class="compare-row-val" style="color:var(--green)">${bestDate}</span></div>
      <div class="compare-row"><span class="compare-row-label">Years to FIRE</span><span class="compare-row-val" style="color:var(--green)">${formatYears(bestYears)}</span></div>
      <div class="compare-row"><span class="compare-row-label">FIRE Age</span><span class="compare-row-val" style="color:var(--green)">${Math.round(state.age + bestYears)}</span></div>
      <div class="compare-row"><span class="compare-row-label">Freedom Number</span><span class="compare-row-val">${formatCrLakh(bestFN)}</span></div>
      <div class="compare-row"><span class="compare-row-label">Corpus at FIRE</span><span class="compare-row-val">${formatCrLakh(bestCorpus)}</span></div>
    </div>
  `;

  // Summary
  const summaryDiv = document.createElement('div');
  summaryDiv.style.cssText = 'grid-column:1/-1;background:rgba(74,184,122,0.06);border:1px solid rgba(74,184,122,0.2);border-radius:10px;padding:16px;margin-top:4px';
  summaryDiv.innerHTML = `
    <p style="font-family:'DM Mono',monospace;font-size:0.7rem;color:var(--green);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px">Potential Gain</p>
    <p style="font-family:'DM Mono',monospace;font-size:1.1rem;color:var(--green)">⚡ ${formatYears(Math.max(0, diff))} earlier retirement · ${formatCrLakh(Math.abs(results.corpusAtFire - bestCorpus))} ${bestCorpus > results.corpusAtFire ? 'more' : 'less'} corpus</p>
    <p style="font-size:0.75rem;color:var(--text-muted);margin-top:6px">Best case assumes: +₹25K/mo extra savings, 20% income raise, 20% expense cut, 1.5% extra returns.</p>
  `;
  el.appendChild(summaryDiv);
}

// ===================== ANIMATE TEXT =====================
function animateText(id, val) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.add('counting');
  el.textContent = val;
  setTimeout(() => el.classList.remove('counting'), 200);
}

// ===================== INIT =====================
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="range"]').forEach(el => {
    updateSliderFill(el);
    el.addEventListener('input', () => updateSliderFill(el));
  });

  // Activate first field
  setTimeout(() => {
    const fieldAge = document.getElementById('fieldAge');
    if (fieldAge) fieldAge.classList.add('active');
  }, 100);
});

window.addEventListener('resize', () => {
  if (document.getElementById('resultsPage').classList.contains('active')) {
    renderCorpusChart();
  }
});