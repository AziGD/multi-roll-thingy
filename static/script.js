const socket = io();
let username = "";

function signup() {
    username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/signup', {
        method: 'POST',
        body: new URLSearchParams({username, password})
    }).then(res => res.json())
      .then(data => alert(data.message));
}

function login() {
    username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        body: new URLSearchParams({username, password})
    }).then(res => res.json())
      .then(data => {
          if(data.status === "success") {
              alert(data.message);
              document.getElementById('auth').style.display = "none";
              document.getElementById('game').style.display = "block";
          } else {
              alert(data.message);
          }
      });
}

function joinGame() {
    socket.emit('join', {name: username});
}

function roll() {
    socket.emit('roll', {name: username});
}

socket.on('roll_result', data => {
    const div = document.getElementById('messages');
    div.innerHTML += `<p>${data.message}</p>`;
});

socket.on('system_message', data => {
    const div = document.getElementById('messages');
    div.innerHTML += `<p><b>${data}</b></p>`;
});

socket.on('special_cutscene', data => {
    alert(data.message);
});
