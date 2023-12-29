const APP_CONTAINER = document.getElementById("app");
let posX = 50;
let posY = 50;
let name, team, canvas, state;
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
    <div id="points">0:0</div>
    <canvas id="game" width="${width}px" height="${height}px" style="background-image: url('assets/map.jpg');">
    
    </canvas>
    <div id="dead"></div>
    `;

  canvas = document.getElementById("game");
  let direction = 0,
    rad = 0;
  function handleMouseMove(event) {
    if (rad != direction) {
      direction = rad;
      fetch(`/set-direction?name=${name}`, {
        method: "POST",
        body: JSON.stringify({ direction }),
        headers: { "Content-Type": "application/json" },
      });
    }
  }

  canvas.addEventListener("mousemove", (event) => {
    if (state)
      state.players.forEach((element) => {
        if (element.name == name) {
          let deltaX = event.offsetX - element.x;
          let deltaY = event.offsetY - element.y;
          rad = Math.atan2(deltaY, deltaX);
        }
      });
  });
  setInterval(handleMouseMove, 100);
}

const source = new EventSource(`/events`);

source.addEventListener("state", (e) => {
  render(JSON.parse(e.data));
  state = JSON.parse(e.data);
  console.log(state);
  console.log(JSON.parse(e.data));
});

function render(state) {
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  document.getElementById("points").innerHTML = `${state.points.Red}:${state.points.Blue}`
  document.getElementById("dead").innerHTML=``;
  let flag_in_base = {Red: true, Blue: true}
  state.players.forEach((element) => {
    if (!element.died_at) {
      
      context.beginPath();
      context.arc(element.x, element.y, 10, 0, 2 * Math.PI);
      context.fillStyle = element.team;
      context.fill();
      context.fillStyle = "black";
      context.font = "20px serif";
      context.fillText(
        element.name,
        element.x - context.measureText(element.name).width / 2,
        element.y + 25
      );
      if (element.has_flag) {
        context.font = "bold 22px arial";
        context.fillStyle = "white";
        context.fillText("x", element.x-6, element.y+6);
        flag_in_base[element.team] = false;
      }
      context.strokeStyle = element.name == name ? "white" : "#222222";
      context.lineWidth = 3;
      context.stroke();
    } else if (element.name == name){
       document.getElementById("dead").innerHTML=`You are dead, respawning in 10 seconds`
    }
  });
    if (flag_in_base.Red) {
            context.fillStyle = "white";
            context.font = "bold 100px arial";
            context.fillText("X", canvas.width-70, canvas.height/2+30);
    }
    if (flag_in_base.Blue) {
        context.fillStyle = "white";
        context.font = "bold 100px arial";
        context.fillText("X", 5, canvas.height/2+30);
    }
}
