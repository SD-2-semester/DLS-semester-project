package main

import (
	"log"
)

func main() {
	log.Printf("Starting user service...\n")

	store, err := NewPostgresStore()
	if err != nil {
		log.Fatal(err)
	}

	if err := store.Init(); err != nil {
		log.Fatal(err)
	}

	publisher, err := NewRabbitMQPublisher()
	if err != nil {
		log.Fatal(err)
	}

	server := NewAPIServer(":8080", store, publisher)
	server.Run()
}
