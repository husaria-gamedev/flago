const appContainer = document.getElementById("app");
let name, team;
appContainer.innerHTML = `
<img src="assets/logo.png" style="width: 500px;"/><br/>
<input type="text" id="username"/>
<button onclick="test()">Next</button>
`;

function test() {
    name = document.getElementById("username").value;
    appContainer.innerHTML = `
    <img src="assets/logo.svg" />
    <button onclick="chooseTeam('Red')">Red</button>
    <button onclick="chooseTeam('Blue')">Blue</button><br/>
    <button onclick="play()">Play</button>
    `;
}

function chooseTeam(t) {
    team = t;
}

function play() {
    fetch("http://127.0.0.1:5000/register", {
        method: "POST", 
        body: JSON.stringify({name, team}), 
        headers: {"Content-Type": "application/json"}
    })
    console.log(name, team)
}
