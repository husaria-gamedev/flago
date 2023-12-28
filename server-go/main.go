package main

import (
	"io"
	"net/http"
	"server-go/server-go/game"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

var state = game.State{}

func main() {
	r := gin.Default()

	r.Use(cors.Default())

	updatesChan := newUpdatesChan()

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
			Team:    game.Team(reg.Team),
		})
		c.JSON(http.StatusOK, game.RegistrationResponse{Id: playerId, RegistrationRequest: reg})
	})

	r.GET("/events", func(c *gin.Context) {
		c.Stream(func(w io.Writer) bool {
			// Stream message to client from message channel
			state := <-updatesChan
			c.SSEvent("message", state)
			return true
		})
	})

	r.Run(":5000") // listen and serve on 0.0.0.0:8080 (for windows "localhost:8080")
}

func newUpdatesChan() chan game.State {
	c := make(chan game.State)

	go func() {
		for {
			c <- state
			time.Sleep(time.Millisecond * 50)
		}
	}()

	return c
}
