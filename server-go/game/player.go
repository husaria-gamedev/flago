package game

type Player struct {
	X       int
	Y       int
	IsAlive bool
	HasFlag bool
	Name    string
	Team    Team
}

type Team string

const (
	TeamRed  Team = "Red"
	TeamBlue Team = "Blue"
)
