let socket = null;
let isTranslating = false;
let currentTargetLang = "deu";

chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
    if (message.action === "start_translation") {
        currentTargetLang = message.targetLang || "deu";
        await startTranslation();
        sendResponse({ status: "starting" });
    } else if (message.action === "stop_translation") {
        stopTranslation();
        sendResponse({ status: "stopping" });
    } else if (message.type === "audio-data") {
        if (socket && socket.readyState === WebSocket.OPEN) {
            // Chunking or buffering could be done here if needed
            // Currently sending raw PCM chunks from offscreen
            const pcmData = new Int16Array(message.data);
            socket.send(pcmData.buffer);
        }
    }
});

async function startTranslation() {
    if (isTranslating) return;

    socket = new WebSocket("ws://localhost:5000/api/ws/translate");

    socket.onopen = async () => {
        console.log("Connected to translation server.");
        isTranslating = true;

        // Handshake or init message with target language
        socket.send(JSON.stringify({ type: "init", target_lang: currentTargetLang }));

        const streamId = await chrome.tabCapture.getMediaStreamId();
        await setupOffscreenDocument(streamId);

        chrome.runtime.sendMessage({ action: "status_update", status: "connected" });
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.text) {
                chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                    if (tabs[0]) {
                        chrome.tabs.sendMessage(tabs[0].id, { action: "display_translation", text: data.text });
                    }
                });
            }
        } catch (e) {
            // Might be binary data (translated audio) - skipped for text-only demo
        }
    };

    socket.onclose = () => {
        console.log("Disconnected from translation server.");
        isTranslating = false;
        chrome.runtime.sendMessage({ action: "status_update", status: "disconnected" });
        // Clean up offscreen
        chrome.offscreen.closeDocument();
    };

    socket.onerror = (err) => {
        console.error("WebSocket error:", err);
        stopTranslation();
    };
}

async function setupOffscreenDocument(streamId) {
    if (await chrome.offscreen.hasDocument()) return;

    await chrome.offscreen.createDocument({
        url: 'offscreen.html',
        reasons: ['USER_MEDIA'],
        justification: 'Capture tab audio for real-time translation.'
    });

    // Need to wait a bit for offscreen to be ready before sending message
    setTimeout(() => {
        chrome.runtime.sendMessage({
            type: 'start-capture',
            target: 'offscreen',
            data: streamId
        });
    }, 500);
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
