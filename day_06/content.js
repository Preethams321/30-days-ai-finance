(() => {
  let container = null;
  let tick = null;

  const getState = () => new Promise((resolve) => {
    chrome.storage.local.get(null, resolve);
  });

  function create() {
    if (container) return;

    container = document.createElement("div");
    container.style.position = "fixed";
    container.style.right = "16px";
    container.style.bottom = "16px";
    container.style.zIndex = "2147483647";
    container.style.background = "rgba(0,0,0,0.85)";
    container.style.color = "#f5f5f5";
    container.style.fontFamily = "system-ui, -apple-system, BlinkMacSystemFont, sans-serif";
    container.style.borderRadius = "14px";
    container.style.border = "1px solid #3a3a3a";
    container.style.padding = "8px 10px";
    container.style.minWidth = "160px";
    container.style.boxShadow = "0 12px 30px rgba(0,0,0,0.6)";
    container.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span id="byofocus-title" style="font-size:11px;color:#b3b3b3;">Focus</span>
        <button id="byofocus-hide" style="background:none;border:none;color:#777;font-size:11px;cursor:pointer;">Hide</button>
      </div>
      <div id="byofocus-time" style="font-size:20px;font-weight:500;margin-top:2px;">25:00</div>
      <div id="byofocus-mode" style="font-size:11px;color:#9a9a9a;margin-top:2px;">idle</div>
      <div style="display:flex;gap:6px;margin-top:6px;">
        <button id="byofocus-start" style="flex:1;border-radius:999px;border:1px solid #f5f5f5;background:#f5f5f5;color:#000;font-size:11px;padding:4px 6px;cursor:pointer;">Start</button>
        <button id="byofocus-stop" style="flex:1;border-radius:999px;border:1px solid #555;background:transparent;color:#ccc;font-size:11px;padding:4px 6px;cursor:pointer;">Stop</button>
      </div>
    `;
    document.documentElement.appendChild(container);

    container.querySelector("#byofocus-hide").onclick = async () => {
      await chrome.storage.local.set({ showWidget: false });
      destroy();
    };

    container.querySelector("#byofocus-start").onclick = () => {
      chrome.runtime.sendMessage({ type: "START_FOCUS" });
    };

    container.querySelector("#byofocus-stop").onclick = () => {
      chrome.runtime.sendMessage({ type: "STOP_POMODORO" });
    };
  }

  function destroy() {
    if (container) {
      container.remove();
      container = null;
    }
    if (tick) {
      clearInterval(tick);
      tick = null;
    }
  }

  async function render() {
    const state = await getState();
    if (!state.showWidget || !state.onboardingComplete) {
      destroy();
      return;
    }

    create();

    const title = container.querySelector("#byofocus-title");
    const time = container.querySelector("#byofocus-time");
    const mode = container.querySelector("#byofocus-mode");

    const name = state.userName || "Your";
    title.textContent = `${name}'s focus`;

    const p = state.pomodoro || {};
    if (p.isRunning && p.endsAt) {
      const ms = Math.max(0, p.endsAt - Date.now());
      const sec = Math.ceil(ms / 1000);
      const m = String(Math.floor(sec / 60)).padStart(2, "0");
      const s = String(sec % 60).padStart(2, "0");
      time.textContent = `${m}:${s}`;
      mode.textContent = p.mode || "running";
    } else {
      const mins = state.focusMinutes || 25;
      time.textContent = `${String(mins).padStart(2, "0")}:00`;
      mode.textContent = "idle";
    }
  }

  chrome.storage.onChanged.addListener(() => {
    render();
  });

  render();
  tick = setInterval(render, 1000);
})();