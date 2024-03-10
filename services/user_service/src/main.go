package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	"github.com/gorilla/mux"
)

func main() {
	a := App{}
	a.Initialize(
		os.Getenv("APP_DB_USERNAME"),
		os.Getenv("APP_DB_PASSWORD"),
		os.Getenv("APP_DB_NAME"),
	)

	a.Run(":8080")

	r := mux.NewRouter()

	srv := &http.Server{
		Handler:      r,
		Addr:         "localhost:8080",
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil {
			log.Println(err)
		}
	}()

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	// block until a signal is received.
	<-c

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	srv.Shutdown(ctx)

	log.Println("shutting down")
}
