const toggleBtn = document.getElementById('toggleBtn');
const statusDiv = document.getElementById('status');

let isRunning = false;

// Check initial status
chrome.storage.local.get(['isTranslating'], (result) => {
    isRunning = !!result.isTranslating;
    updateUI();
});

toggleBtn.addEventListener('click', () => {
    if (!isRunning) {
        chrome.runtime.sendMessage({ action: "start_translation" }, (response) => {
            isRunning = true;
            chrome.storage.local.set({ isTranslating: true });
            updateUI();
        });
    } else {
        chrome.runtime.sendMessage({ action: "stop_translation" }, (response) => {
            isRunning = false;
            chrome.storage.local.set({ isTranslating: false });
            updateUI();
        });
    }
});

chrome.runtime.onMessage.addListener((message) => {
    if (message.action === "status_update") {
        statusDiv.textContent = message.status.charAt(0).toUpperCase() + message.status.slice(1);
        if (message.status === "disconnected") {
            isRunning = false;
            chrome.storage.local.set({ isTranslating: false });
            updateUI();
        }
    }
});

function updateUI() {
    toggleBtn.textContent = isRunning ? "Stop Translation" : "Start Translation";
    toggleBtn.className = isRunning ? "btn stop" : "btn";
}
