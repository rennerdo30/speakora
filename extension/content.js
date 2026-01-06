console.log("SeamlessM4T Content Script Loaded.");

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "display_translation") {
        showOverlay(message.text);
    }
});

const OVERLAY_ID = 's2st-overlay';

function createOverlay() {
    const overlay = document.createElement('div');
    overlay.id = OVERLAY_ID;
    overlay.style.cssText = `
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(15, 23, 42, 0.9);
        color: #f8fafc;
        padding: 16px 24px;
        border-radius: 12px;
        z-index: 2147483647; /* Max z-index */
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 18px;
        line-height: 1.5;
        font-weight: 500;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        transition: opacity 0.3s ease, transform 0.3s ease;
        opacity: 0;
        pointer-events: auto;
        cursor: grab;
        max-width: 80vw;
        text-align: center;
        user-select: none;
    `;

    // Add drag functionality
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    overlay.addEventListener("mousedown", dragStart);
    document.addEventListener("mouseup", dragEnd);
    document.addEventListener("mousemove", drag);

    function dragStart(e) {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        if (e.target === overlay) {
            isDragging = true;
        }
    }

    function dragEnd(e) {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            xOffset = currentX;
            yOffset = currentY;
            // Respect the initial centered transform when dragging? 
            // Actually it's easier to remove generic transform and use top/left if dragging
            // But let's keep it simple: translate3d
            setTranslate(currentX, currentY, overlay);
        }
    }

    function setTranslate(xPos, yPos, el) {
        // Maintain the initial centering (-50% X) plus drag offset
        el.style.transform = `translate(calc(-50% + ${xPos}px), ${yPos}px)`;
    }

    document.body.appendChild(overlay);
    return overlay;
}

function showOverlay(text) {
    let overlay = document.getElementById(OVERLAY_ID);
    if (!overlay) {
        overlay = createOverlay();
    }

    overlay.textContent = text;
    overlay.style.opacity = '1';

    // Auto-hide after 5 seconds if no new text
    if (overlay.timeout) clearTimeout(overlay.timeout);
    overlay.timeout = setTimeout(() => {
        overlay.style.opacity = '0';
        // Optional: remove from DOM to clean up, or keep hidden
        // overlay.timeout = setTimeout(() => overlay.remove(), 300); 
    }, 5000);
}
