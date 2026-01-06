console.log("SeamlessM4T Content Script Loaded.");

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "display_translation") {
        showOverlay(message.text);
    }
});

function showOverlay(text) {
    let overlay = document.getElementById('s2st-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 's2st-overlay';
        overlay.style.cssText = `
      position: fixed;
      bottom: 50px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px 20px;
      border-radius: 8px;
      z-index: 10000;
      font-family: sans-serif;
      font-size: 18px;
      backdrop-filter: blur(4px);
      border: 1px solid rgba(255, 255, 255, 0.2);
    `;
        document.body.appendChild(overlay);
    }
    overlay.textContent = text;

    // Auto-hide after 5 seconds if no new text
    clearTimeout(overlay.timeout);
    overlay.timeout = setTimeout(() => {
        overlay.remove();
    }, 5000);
}
