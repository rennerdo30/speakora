const toggleBtn = document.getElementById('toggleBtn');
const btnText = document.getElementById('btnText');
const btnIcon = document.getElementById('btnIcon');
const statusText = document.getElementById('statusText');
const statusDot = document.getElementById('statusDot');
const targetLangSelect = document.getElementById('targetLang');

let isRunning = false;

// Load persisted state
chrome.storage.local.get(['isTranslating', 'targetLang'], (result) => {
    isRunning = !!result.isTranslating;
    if (result.targetLang) {
        targetLangSelect.value = result.targetLang;
    }
    updateUI();
});

// Save language preference on change
targetLangSelect.addEventListener('change', () => {
    chrome.storage.local.set({ targetLang: targetLangSelect.value });
});

toggleBtn.addEventListener('click', () => {
    if (!isRunning) {
        const targetLang = targetLangSelect.value;
        chrome.runtime.sendMessage({
            action: "start_translation",
            targetLang: targetLang
        }, (response) => {
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
        statusText.textContent = message.status.charAt(0).toUpperCase() + message.status.slice(1);
        if (message.status === "connected") {
            statusDot.className = "dot active";
        } else {
            statusDot.className = "dot";
            if (message.status === "disconnected") {
                isRunning = false;
                chrome.storage.local.set({ isTranslating: false });
                updateUI();
            }
        }
    }
});

function updateUI() {
    if (isRunning) {
        btnText.textContent = "Stop Translation";
        btnIcon.textContent = "■";
        toggleBtn.className = "btn stop";
        targetLangSelect.disabled = true;
    } else {
        btnText.textContent = "Start Translation";
        btnIcon.textContent = "▶";
        toggleBtn.className = "btn";
        targetLangSelect.disabled = false;
    }
}
