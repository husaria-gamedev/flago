package main

import (
	"net/http"
	"server-go/game"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

var state = game.State{}

var connections = []*gin.Context{}

func main() {
	r := gin.Default()

	r.Use(cors.Default())

	startGame()

	r.POST("/register", func(c *gin.Context) {
		var reg game.RegistrationRequest

		err := c.BindJSON(&reg)
		if err != nil {
			panic(err)
		}

		playerId := len(state.Players)
		state.Players = append(state.Players, game.Player{
			X:       500,
			Y:       500,
			IsAlive: true,
			HasFlag: false,
			Name:    reg.Name,
			Team:    reg.Team,
		})
		c.JSON(http.StatusOK, game.RegistrationResponse{Id: playerId, RegistrationRequest: reg})
	})

	r.GET("/events", func(c *gin.Context) {
		connections = append(connections, c)
		<-c.Writer.CloseNotify()
	})

	r.Run(":5000") // listen and serve on 0.0.0.0:8080 (for windows "localhost:8080")
}

func startGame() {
	go func() {
		for {
			time.Sleep(time.Millisecond * 100)
			broadcastState(state)
		}
	}()
}

func broadcastState(s game.State) {
	for _, c := range connections {
		c.SSEvent("state", s)
		c.Writer.Flush()
	}
}
