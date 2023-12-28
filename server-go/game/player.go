package game

type Player struct {
	X int
	Y int
	IsAlive bool
	HasFlag bool
	Team Team
}

type Team string

const (
	TeamRed = "Red"
	TeamBlue = "Blue"
)