const $ = (id) => document.getElementById(id);

const onboardingCard = $("onboardingCard");
const mainCard = $("mainCard");

document.addEventListener("DOMContentLoaded", async () => {
  bindEvents();
  await render();
  startLiveTimer();
});

function sendMessage(type, payload = {}) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type, payload }, (res) => {
      resolve(res || { ok: false });
    });
  });
}

function bindEvents() {
  $("saveSetupBtn").addEventListener("click", async () => {
    await sendMessage("SAVE_ONBOARDING", {
      userName: $("nameInput").value.trim(),
      dailyGoalMinutes: Number($("goalInput").value || 120),
      focusMinutes: Number($("focusInput").value || 25),
      shortBreakMinutes: Number($("shortBreakInput").value || 5),
      longBreakMinutes: Number($("longBreakInput").value || 15),
      safeModeAdult: $("safeModeSetup").checked
    });
    await render();
  });

  $("saveIntentionBtn").addEventListener("click", async () => {
    const txt = $("intentionInput").value.trim();
    await sendMessage("SAVE_INTENTION", { intention: txt });
    $("intentionStatus").textContent = "Saved for today.";
  });

  $("startFocusBtn").addEventListener("click", async () => {
    await sendMessage("START_FOCUS");
    await render();
  });

  $("startBreakBtn").addEventListener("click", async () => {
    await sendMessage("START_BREAK");
    await render();
  });

  $("stopBtn").addEventListener("click", async () => {
    await sendMessage("STOP_POMODORO");
    await render();
  });

  $("saveTimerSettingsBtn").addEventListener("click", async () => {
    await sendMessage("UPDATE_SETTINGS", {
      focusMinutes: Number($("focusSettingInput").value || 25),
      shortBreakMinutes: Number($("shortBreakSettingInput").value || 5),
      longBreakMinutes: Number($("longBreakSettingInput").value || 15)
    });
    await render();
  });

  $("shortsToggle").addEventListener("change", async (e) => {
    await sendMessage("TOGGLE_SHORTS", { enabled: e.target.checked });
  });

  $("safeModeToggle").addEventListener("change", async (e) => {
    await sendMessage("TOGGLE_SAFE_MODE", { enabled: e.target.checked });
  });

  $("widgetToggle").addEventListener("change", async (e) => {
    await sendMessage("TOGGLE_WIDGET", { enabled: e.target.checked });
  });

  $("addDomainBtn").addEventListener("click", async () => {
    const value = $("domainInput").value.trim();
    if (!value) return;
    await sendMessage("ADD_BLOCKED_DOMAIN", { domain: value });
    $("domainInput").value = "";
    await render();
  });
}

async function render() {
  const res = await sendMessage("GET_STATE");
  if (!res.ok || !res.state) return;
  const state = res.state;

  if (!state.onboardingComplete) {
    onboardingCard.classList.remove("hidden");
    mainCard.classList.add("hidden");

    $("nameInput").value = state.userName || "";
    $("goalInput").value = state.dailyGoalMinutes || 120;
    $("focusInput").value = state.focusMinutes || 25;
    $("shortBreakInput").value = state.shortBreakMinutes || 5;
    $("longBreakInput").value = state.longBreakMinutes || 15;
    $("safeModeSetup").checked = !!state.safeModeAdult;

    return;
  }

  onboardingCard.classList.add("hidden");
  mainCard.classList.remove("hidden");

  const name = state.userName || "Your";
  $("heroTitle").textContent = `${name}'s Focus`;
  $("heroSubtitle").textContent = `Daily target: ${state.dailyGoalMinutes} minutes`;

  // Intention
  if (state.intentionDate === todayStr()) {
    $("intentionInput").value = state.intention || "";
  } else {
    $("intentionInput").value = "";
  }
  $("intentionStatus").textContent = "";

  // Toggles
  $("shortsToggle").checked = !!state.blockShorts;
  $("safeModeToggle").checked = !!state.safeModeAdult;
  $("widgetToggle").checked = state.showWidget !== false;

  // Pomodoro
  renderPomodoro(state);

  // Settings fields
  $("focusSettingInput").value = state.focusMinutes || 25;
  $("shortBreakSettingInput").value = state.shortBreakMinutes || 5;
  $("longBreakSettingInput").value = state.longBreakMinutes || 15;

  // Stats
  const s = state.stats || {};
  $("streakValue").textContent = `${s.streakDays || 0} day${s.streakDays === 1 ? "" : "s"}`;
  $("todayValue").textContent = `${s.todayFocusMinutes || 0} min`;
  $("sessionsValue").textContent = String(s.todaySessions || 0);
  $("levelValue").textContent = String(s.level || 1);

  // Domains
  renderDomains(state.blockedDomains || []);
}

function renderPomodoro(state) {
  const p = state.pomodoro || {};
  const badge = $("modeBadge");
  const display = $("timerDisplay");
  const sub = $("timerSubtext");

  if (p.isRunning && p.endsAt) {
    const ms = Math.max(0, p.endsAt - Date.now());
    const sec = Math.ceil(ms / 1000);
    const m = String(Math.floor(sec / 60)).padStart(2, "0");
    const s = String(sec % 60).padStart(2, "0");
    display.textContent = `${m}:${s}`;
  } else {
    const mins = state.focusMinutes || 25;
    display.textContent = `${String(mins).padStart(2, "0")}:00`;
  }

  badge.textContent = p.mode || "idle";

  if (!p.isRunning || p.mode === "idle") {
    sub.textContent = "Ready when you are.";
  } else if (p.mode === "focus") {
    sub.textContent = "Deep focus in progress.";
  } else {
    sub.textContent = "Break in progress.";
  }
}

function renderDomains(domains) {
  const list = $("domainList");
  list.innerHTML = "";
  domains.forEach((d) => {
    const li = document.createElement("li");
    li.className = "site-item";
    const span = document.createElement("span");
    span.textContent = d;
    const btn = document.createElement("button");
    btn.className = "btn-ghost";
    btn.textContent = "Remove";
    btn.style.fontSize = "11px";
    btn.addEventListener("click", async () => {
      await sendMessage("REMOVE_BLOCKED_DOMAIN", { domain: d });
      await render();
    });
    li.appendChild(span);
    li.appendChild(btn);
    list.appendChild(li);
  });
}

function startLiveTimer() {
  setInterval(async () => {
    const res = await sendMessage("GET_STATE");
    if (!res.ok || !res.state || !res.state.onboardingComplete) return;
    renderPomodoro(res.state);
  }, 1000);
}

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}