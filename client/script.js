const APP_CONTAINER = document.getElementById("app");
const SERVER_ADDRESS = "http://localhost:5000";
let posX = 50;
let posY = 50;
let name, team, canvas;
APP_CONTAINER.innerHTML = `
<img src="assets/logo.png" style="width: 250px;"/><br/>
<input required placeholder="Type your name" type="text" id="username"/><br/>
<button class="next" onclick="next()">Next</button>
`;

function next() {
  name = document.getElementById("username").value;
  APP_CONTAINER.innerHTML = `
    <img src="assets/logo.png" style="width: 350px;"/><br/>
    <div class="flag_container">
        <button class="team" id="redButton" onclick="chooseTeam('Red')">
        <img src="assets/red_flag.svg" alt="Red Flag"/>
        </button>
        <button class="team" id="blueButton" onclick="chooseTeam('Blue')">
        <img src="assets/blue_flag.svg" alt="Blue Flag"/>
        </button>
    </div><br/>
    <button class="next" onclick="play()">Play</button>
    `;
}

function chooseTeam(t) {
  document.getElementById("redButton").classList.remove("active");
  document.getElementById("blueButton").classList.remove("active");

  // Add active class to the clicked button
  event.currentTarget.classList.add("active");
  team = t;
}

function play() {
  fetch(`${SERVER_ADDRESS}/register`, {
    method: "POST",
    body: JSON.stringify({ name, team }),
    headers: { "Content-Type": "application/json" },
  });
  const width = 1000;
  const height = 500;
  APP_CONTAINER.innerHTML = `
    <canvas id="game" width="${width}px" height="${height}px" style="background: white;">
    
    </canvas>
    `;
  canvas = document.getElementById("game");

  canvas.addEventListener("mousemove", (event) => {
    let deltaX = event.offsetX - posX;
    let deltaY = event.offsetY - posY;
    let rad = Math.atan2(deltaY, deltaX);
    fetch(`${SERVER_ADDRESS}/set-direction?name=${name}`, {
      method: "POST",
      body: JSON.stringify({ direction: rad }),
      headers: { "Content-Type": "application/json" },
    });
  });
}

const source = new EventSource(`${SERVER_ADDRESS}}/events`);

source.onmessage = (event) => {

  console.log(event);
};

function render(state) {
  
}
