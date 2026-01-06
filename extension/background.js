let socket = null;
let isTranslating = false;

chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
    if (message.action === "start_translation") {
        await startTranslation();
        sendResponse({ status: "starting" });
    } else if (message.action === "stop_translation") {
        stopTranslation();
        sendResponse({ status: "stopping" });
    } else if (message.type === "audio-data") {
        if (socket && socket.readyState === WebSocket.OPEN) {
            // Convert Array to Int16Array then to Buffer
            const pcmData = new Int16Array(message.data);
            socket.send(pcmData.buffer);
        }
    }
});

async function startTranslation() {
    if (isTranslating) return;

    // 1. Setup WebSocket
    socket = new WebSocket("ws://localhost:5000/api/ws/translate");

    socket.onopen = async () => {
        console.log("Connected to translation server.");
        isTranslating = true;

        // 2. Start Tab Capture
        const streamId = await chrome.tabCapture.getMediaStreamId();
        await setupOffscreenDocument(streamId);

        chrome.runtime.sendMessage({ action: "status_update", status: "connected" });
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.status === "processing") {
            // Potentially update status
        } else if (data.text) {
            // Send text to content script to display overlay
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                if (tabs[0]) {
                    chrome.tabs.sendMessage(tabs[0].id, { action: "display_translation", text: data.text });
                }
            });
        }
    };

    socket.onclose = () => {
        console.log("Disconnected from translation server.");
        isTranslating = false;
        chrome.runtime.sendMessage({ action: "status_update", status: "disconnected" });
    };
}

async function setupOffscreenDocument(streamId) {
    if (await chrome.offscreen.hasDocument()) return;

    await chrome.offscreen.createDocument({
        url: 'offscreen.html',
        reasons: ['USER_MEDIA'],
        justification: 'Capture tab audio for real-time translation.'
    });

    chrome.runtime.sendMessage({
        type: 'start-capture',
        target: 'offscreen',
        data: streamId
    });
}

function stopTranslation() {
    if (socket) {
        socket.close();
        socket = null;
    }
    isTranslating = false;

    chrome.runtime.sendMessage({
        type: 'stop-capture',
        target: 'offscreen'
    });
}
