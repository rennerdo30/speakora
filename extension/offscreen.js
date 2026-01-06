chrome.runtime.onMessage.addListener(async (message) => {
    if (message.target !== 'offscreen') return;

    if (message.type === 'start-capture') {
        startCapture(message.data);
    } else if (message.type === 'stop-capture') {
        stopCapture();
    }
});

let recorder;
let audioContext;
let processor;

async function startCapture(streamId) {
    if (recorder) return;

    const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
            mandatory: {
                chromeMediaSource: 'tab',
                chromeMediaSourceId: streamId
            }
        },
        video: false
    });

    // Continue to play the audio locally so the user can hear it
    audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(audioContext.destination);

    // Use a ScriptProcessor or AudioWorklet to get raw audio data
    // For simplicity and compatibility, we use ScriptProcessor for now
    processor = audioContext.createScriptProcessor(4096, 1, 1);
    source.connect(processor);
    processor.connect(audioContext.destination);

    processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        // Convert Float32 to Int16 PCM
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
        }

        // Send PCM data back to background script to be forwarded to WebSocket
        chrome.runtime.sendMessage({
            type: 'audio-data',
            data: Array.from(pcmData)
        });
    };
}

function stopCapture() {
    if (processor) {
        processor.disconnect();
        processor = null;
    }
    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }
    window.close();
}
