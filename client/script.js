const APP_CONTAINER = document.getElementById("app");
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
  fetch(`/register`, {
    method: "POST",
    body: JSON.stringify({ team, name }),
    headers: { "Content-Type": "application/json" },
  });
  const width = 1000;
  const height = 500;

  APP_CONTAINER.innerHTML = `
    <canvas id="game" width="${width}px" height="${height}px" style="background: white;">
    
    </canvas>
    `;

  canvas = document.getElementById("game");
  let direction = 0,
    rad = 0;
  function handleMouseMove(event) {
    if (rad != direction) {
      direction = rad
      fetch(`/set-direction?name=${name}`, {
        method: "POST",
        body: JSON.stringify({ direction }),
        headers: { "Content-Type": "application/json" },
      });
    }
  }
  canvas.addEventListener("mousemove", (event) => {
    let deltaX = event.offsetX - posX;
    let deltaY = event.offsetY - posY;
    rad = Math.atan2(deltaY, deltaX);
  });
  setInterval(handleMouseMove, 100);
}

const source = new EventSource(`/events`);

source.addEventListener("state", (e) => {
  render(JSON.parse(e.data))
  console.log(JSON.parse(e.data));
});

function render(state) {
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  
  state.players.forEach(element => {
    context.rect(element.x, element.y, 10, 10);
    context.fill();
  });
  
}
