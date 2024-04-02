package main

import (
	"log"
)

func main() {
	log.Printf("Starting user service...\n")

	readStore, err := NewPostgresStoreRead(
		LoadDBConfig("AUTHSERVICE_RO_"),
	)
	if err != nil {
		log.Fatal(err)
	}

	if err := readStore.Init(); err != nil {
		log.Fatal(err)
	}

	writeStore, err := NewPostgresStoreWrite(
		LoadDBConfig("AUTHSERVICE_WO_"),
	)
	if err != nil {
		log.Fatal(err)
	}

	if err := writeStore.Init(); err != nil {
		log.Fatal(err)
	}

	publisher, err := NewRabbitMQPublisher(
		LoadRabbitMQConfig(),
	)
	if err != nil {
		log.Fatal(err)
	}

	server := NewAPIServer(
		":8080",
		readStore,
		writeStore,
		publisher,
	)
	server.Run()
}
