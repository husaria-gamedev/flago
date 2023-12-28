const appContainer = document.getElementById("app");
let name, team;
appContainer.innerHTML = `
<img src="assets/logo.png" style="width: 250px;"/><br/>
<input placeholder="Type your name" type="text" id="username"/><br/>
<button class="next" onclick="next()">Next</button>
`;

function next() {
    name = document.getElementById("username").value;
    appContainer.innerHTML = `
    <img src="assets/logo.png" style="width: 250px;"/><br/>
    <div>
        <button onclick="chooseTeam('Red')">Red</button>
        <button onclick="chooseTeam('Blue')">Blue</button>
    <div>
    <button class="next" onclick="play()">Play</button>
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

const source = new EventSource("http://localhost:5000/events")

source.onmessage = (event) => {
    console.log(event)
};