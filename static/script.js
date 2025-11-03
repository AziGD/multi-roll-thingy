document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    const joinBtn = document.getElementById("join-btn");
    const rollBtn = document.getElementById("roll-btn");
    const playerNameInput = document.getElementById("player-name");
    const messagesList = document.getElementById("messages");
    const devPanel = document.getElementById("dev-panel");

    // Hide dev panel by default
    devPanel.style.display = "none";

    let playerName = "";

    // Join button click
    joinBtn.addEventListener("click", () => {
        const name = playerNameInput.value.trim();
        if (!name) {
            alert("Please enter a name to join!");
            return;
        }
        playerName = name;
        socket.emit("join", { name: playerName });
    });

    // Roll button click
    rollBtn.addEventListener("click", () => {
        if (!playerName) {
            alert("You need to join first!");
            return;
        }
        socket.emit("roll", { name: playerName });
    });

    // Listen for system messages
    socket.on("system_message", (msg) => {
        addMessage(msg);
    });

    // Listen for roll results
    socket.on("roll_result", (data) => {
        addMessage(data.message);
    });

    // Show dev panel if server says so
    socket.on("dev_panel", (data) => {
        devPanel.style.display = "block";
        addMessage(data.message);
    });

    function addMessage(msg) {
        const li = document.createElement("li");
        li.textContent = msg;
        messagesList.appendChild(li);
        // Scroll to bottom
        messagesList.scrollTop = messagesList.scrollHeight;
    }
});
