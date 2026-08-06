// User click listener
document.getElementById("userInputButton").addEventListener("click", getUserInput, false);

// User Enter key listener
document.getElementById("userInput").addEventListener("keydown", function (event) {
    if (event.key === "Enter" || event.keyCode === 13) {
        event.preventDefault();
        getUserInput();
    }
});

// Expose functions to Eel
eel.expose(addUserMsg);
eel.expose(addAppMsg);

function addUserMsg(msg) {
    if (!msg) return;
    const container = document.getElementById("messages");
    const msgDiv = document.createElement("div");
    msgDiv.className = "message msg-user";
    msgDiv.innerHTML = `<div class="bubble">${escapeHtml(msg)}</div>`;
    container.appendChild(msgDiv);
    scrollToBottom();
}

function addAppMsg(msg) {
    if (!msg) return;
    const container = document.getElementById("messages");
    const msgDiv = document.createElement("div");
    msgDiv.className = "message msg-app";
    // Allow inner HTML for breaks like directory listings, but sanitize script tags if any
    msgDiv.innerHTML = `<div class="bubble">${msg}</div>`;
    container.appendChild(msgDiv);
    scrollToBottom();
}

function getUserInput() {
    const inputEl = document.getElementById("userInput");
    const msg = inputEl.value.trim();
    if (msg.length > 0) {
        inputEl.value = "";
        eel.getUserInput(msg);
    }
}

function scrollToBottom() {
    const container = document.getElementById("messages");
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 50);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}