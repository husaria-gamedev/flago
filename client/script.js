const appContainer = document.getElementById("app");
let username, color;
appContainer.innerHTML = `

<img src="assets/logo.png" style="width: 500px;"/><br/>
<input type="text" id="username"/>
<button onclick="test()">Next</button>
`;

function test() {
    username = document.getElementById("username").value;
    appContainer.innerHTML = `
    <img src="assets/logo.svg" />
    <button onclick="chooseTeam('red')">Red</button>
    <button onclick="chooseTeam('blue')">Blue</button><br/>
    <button onclick="play()">Play</button>
    `;
}

function chooseTeam(team) {
    color = team;
}

function play() {
    console.log(username, color)
}