const DEFAULTS = {
  onboardingComplete: false,
  userName: "",
  intention: "",
  intentionDate: "",
  dailyGoalMinutes: 120,
  focusMinutes: 25,
  shortBreakMinutes: 5,
  longBreakMinutes: 15,
  blockedDomains: ["twitter.com", "x.com", "instagram.com", "reddit.com"],
  safeModeAdult: false,
  blockShorts: true,
  focusMode: false,
  showWidget: true,
  pomodoro: {
    mode: "idle", // "idle" | "focus" | "shortBreak" | "longBreak"
    isRunning: false,
    startedAt: null,
    endsAt: null
  },
  stats: {
    totalFocusMinutes: 0,
    todayFocusMinutes: 0,
    todaySessions: 0,
    streakDays: 0,
    longestStreak: 0,
    xp: 0,
    level: 1,
    lastFocusDate: ""
  }
};

const ADULT_DOMAINS = [
  "pornhub.com",
  "xvideos.com",
  "xnxx.com",
  "redtube.com",
  "youporn.com",
  "xhamster.com",
  "spankbang.com"
];

const POMODORO_ALARM = "byofocus_pomodoro";

chrome.runtime.onInstalled.addListener(async () => {
  await ensureDefaults();
});

chrome.runtime.onStartup.addListener(async () => {
  await ensureDefaults();
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (!changeInfo.url && !tab.url) return;

  const url = changeInfo.url || tab.url;
  if (!url || !url.startsWith("http")) return;

  const state = await getState();
  const domain = extractDomain(url);

  // Shorts blocking (always on if enabled)
  if (state.blockShorts && /https?:\/\/(www\.)?youtube\.com\/shorts/i.test(url)) {
    redirectToBlocked(tabId, "shorts", url, state.userName, state.intention);
    return;
  }

  // Adult safe mode
  if (state.safeModeAdult && ADULT_DOMAINS.includes(domain)) {
    redirectToBlocked(tabId, "adult", url, state.userName, state.intention);
    return;
  }

  // Focus mode custom blocked
  if (state.focusMode && state.blockedDomains.includes(domain)) {
    redirectToBlocked(tabId, "focus", url, state.userName, state.intention);
    return;
  }
});

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== POMODORO_ALARM) return;

  const state = await getState();
  const p = state.pomodoro;

  if (!p.isRunning || !p.endsAt) return;
  if (Date.now() < p.endsAt) return;

  // Session completed
  if (p.mode === "focus") {
    const minutes = Math.max(
      1,
      Math.round((p.endsAt - p.startedAt) / 60000)
    );
    const updatedStats = updateStats(state.stats, minutes);

    await chrome.storage.local.set({
      stats: updatedStats,
      pomodoro: {
        mode: "idle",
        isRunning: false,
        startedAt: null,
        endsAt: null
      },
      focusMode: false
    });
  } else {
    await chrome.storage.local.set({
      pomodoro: {
        mode: "idle",
        isRunning: false,
        startedAt: null,
        endsAt: null
      }
    });
  }

  await chrome.alarms.clear(POMODORO_ALARM);
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      switch (message.type) {
        case "GET_STATE": {
          const state = await getState();
          sendResponse({ ok: true, state });
          break;
        }

        case "SAVE_ONBOARDING": {
          const p = message.payload || {};
          await chrome.storage.local.set({
            onboardingComplete: true,
            userName: (p.userName || "").trim(),
            dailyGoalMinutes: toNumber(p.dailyGoalMinutes, 120),
            focusMinutes: toNumber(p.focusMinutes, 25),
            shortBreakMinutes: toNumber(p.shortBreakMinutes, 5),
            longBreakMinutes: toNumber(p.longBreakMinutes, 15),
            safeModeAdult: !!p.safeModeAdult
          });
          sendResponse({ ok: true });
          break;
        }

        case "SAVE_INTENTION": {
          await chrome.storage.local.set({
            intention: (message.payload?.intention || "").trim(),
            intentionDate: today()
          });
          sendResponse({ ok: true });
          break;
        }

        case "START_FOCUS": {
          await startPomodoro("focus");
          sendResponse({ ok: true });
          break;
        }

        case "START_BREAK": {
          await startPomodoro("break");
          sendResponse({ ok: true });
          break;
        }

        case "STOP_POMODORO": {
          await stopPomodoro();
          sendResponse({ ok: true });
          break;
        }

        case "UPDATE_SETTINGS": {
          const p = message.payload || {};
          const updates = {};
          if ("focusMinutes" in p) updates.focusMinutes = toNumber(p.focusMinutes, 25);
          if ("shortBreakMinutes" in p) updates.shortBreakMinutes = toNumber(p.shortBreakMinutes, 5);
          if ("longBreakMinutes" in p) updates.longBreakMinutes = toNumber(p.longBreakMinutes, 15);
          await chrome.storage.local.set(updates);
          sendResponse({ ok: true });
          break;
        }

        case "TOGGLE_SHORTS": {
          await chrome.storage.local.set({ blockShorts: !!message.payload?.enabled });
          sendResponse({ ok: true });
          break;
        }

        case "TOGGLE_SAFE_MODE": {
          await chrome.storage.local.set({ safeModeAdult: !!message.payload?.enabled });
          sendResponse({ ok: true });
          break;
        }

        case "TOGGLE_WIDGET": {
          await chrome.storage.local.set({ showWidget: !!message.payload?.enabled });
          sendResponse({ ok: true });
          break;
        }

        case "ADD_BLOCKED_DOMAIN": {
          const state = await getState();
          const dom = normalizeDomain(message.payload?.domain || "");
          if (!dom) {
            sendResponse({ ok: false, error: "Invalid domain" });
            break;
          }
          const next = Array.from(new Set([...(state.blockedDomains || []), dom]));
          await chrome.storage.local.set({ blockedDomains: next });
          sendResponse({ ok: true, domains: next });
          break;
        }

        case "REMOVE_BLOCKED_DOMAIN": {
          const state = await getState();
          const dom = normalizeDomain(message.payload?.domain || "");
          const next = (state.blockedDomains || []).filter((d) => d !== dom);
          await chrome.storage.local.set({ blockedDomains: next });
          sendResponse({ ok: true, domains: next });
          break;
        }

        default:
          sendResponse({ ok: false, error: "Unknown message type" });
      }
    } catch (err) {
      console.error("runtime.onMessage error", err);
      sendResponse({ ok: false, error: err?.message || "Unknown error" });
    }
  })();

  return true;
});

async function ensureDefaults() {
  const current = await chrome.storage.local.get();
  const merged = deepMerge(DEFAULTS, current);
  await chrome.storage.local.set(merged);
}

async function getState() {
  const state = await chrome.storage.local.get();
  return deepMerge(DEFAULTS, state);
}

async function startPomodoro(kind) {
  const state = await getState();
  const now = Date.now();

  let mode = "focus";
  let minutes = state.focusMinutes || 25;

  if (kind === "break") {
    mode = "shortBreak";
    minutes = state.shortBreakMinutes || 5;
  }

  await chrome.storage.local.set({
    pomodoro: {
      mode,
      isRunning: true,
      startedAt: now,
      endsAt: now + minutes * 60 * 1000
    },
    focusMode: mode === "focus"
  });

  await chrome.alarms.clear(POMODORO_ALARM);
  await chrome.alarms.create(POMODORO_ALARM, { periodInMinutes: 0.25 });
}

async function stopPomodoro() {
  const state = await getState();
  await chrome.alarms.clear(POMODORO_ALARM);
  await chrome.storage.local.set({
    pomodoro: {
      ...state.pomodoro,
      isRunning: false,
      mode: "idle",
      startedAt: null,
      endsAt: null
    },
    focusMode: false
  });
}

function updateStats(statsIn, minutes) {
  const stats = deepMerge(DEFAULTS.stats, statsIn || {});
  const todayStr = today();
  const yesterday = offsetDate(-1);
  const prev = stats.lastFocusDate || "";

  if (prev === todayStr) {
    stats.todayFocusMinutes += minutes;
    stats.todaySessions += 1;
  } else {
    stats.todayFocusMinutes = minutes;
    stats.todaySessions = 1;
  }

  if (prev === yesterday) {
    stats.streakDays = (stats.streakDays || 0) + 1;
  } else if (prev !== todayStr) {
    stats.streakDays = 1;
  }

  stats.longestStreak = Math.max(stats.longestStreak || 0, stats.streakDays || 0);
  stats.totalFocusMinutes += minutes;
  stats.xp += 25;
  stats.level = Math.floor(stats.xp / 100) + 1;
  stats.lastFocusDate = todayStr;

  return stats;
}

function redirectToBlocked(tabId, reason, url, userName, intention) {
  const params = new URLSearchParams({
    reason,
    url,
    user: userName || "",
    intention: intention || ""
  });
  const blockedUrl = `chrome-extension://${chrome.runtime.id}/blocked.html?${params.toString()}`;
  chrome.tabs.update(tabId, { url: blockedUrl });
}

function extractDomain(url) {
  try {
    const u = new URL(url);
    return u.hostname.replace(/^www\./, "").toLowerCase();
  } catch {
    return "";
  }
}

function normalizeDomain(value) {
  return extractDomain(value || "");
}

function toNumber(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) && n > 0 ? n : fallback;
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function offsetDate(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

function deepMerge(base, override) {
  const out = Array.isArray(base) ? [...base] : { ...base };
  for (const key in override) {
    const bv = base?.[key];
    const ov = override[key];
    if (
      bv &&
      ov &&
      typeof bv === "object" &&
      typeof ov === "object" &&
      !Array.isArray(bv) &&
      !Array.isArray(ov)
    ) {
      out[key] = deepMerge(bv, ov);
    } else {
      out[key] = ov;
    }
  }
  return out;
}
