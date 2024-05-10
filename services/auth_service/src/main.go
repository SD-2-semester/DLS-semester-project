package main

import (
	"log"

	_ "github.com/SD-2-semester/DLS-semester-project/services/auth_service/src/docs"
)

// @title API
// @version 1.0
// @description This is a simple auth service.
// @securityDefinitions.apikey ApiKeyAuth
// @in header
// @name Authorization
// @BasePath /api/v1
func main() {
	log.Printf("Starting auth service...\n")

	readStore, err := NewPostgresStoreRead(
		LoadDBConfig("AUTHSERVICE_RO_"),
	)
	if err != nil {
		log.Fatal(err)
	}

	log.Printf("Initializing read storage...\n")
	if err := readStore.Init(); err != nil {
		log.Fatal(err)
	}
	log.Printf("Read storage initialized\n")

	writeStore, err := NewPostgresStoreWrite(
		LoadDBConfig("AUTHSERVICE_WO_"),
	)
	if err != nil {
		log.Fatal(err)
	}

	if err := writeStore.Init(); err != nil {
		log.Fatal(err)
	}

	log.Printf("Write storage initialized\n")

	log.Printf("Initializing rabbitmq messenger...\n")
	messenger, err := NewRMQMessenger(
		LoadRabbitMQConfig(),
	)
	if err != nil {
		log.Fatal(err)
	}

	log.Printf("Rabbitmq messenger initialized\n")

	e := messenger.SubscribeUserCreatedError(writeStore)
	if e != nil {
		log.Fatal(e)
	}

	log.Printf("Subscribed to user created error\n")

	server := NewAPIServer(
		":8080",
		readStore,
		writeStore,
		messenger,
	)
	server.Run()

}
