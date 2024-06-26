package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

const (
	maxRetries = 20
	retryDelay = 2 * time.Second
)

type Messenger interface {
	PublishUserCreated(u *CreateUserPublish) error
	SubscribeUserCreatedError(writeStore WriteStorage) error
}

type RMQMessenger struct {
	conn    *amqp.Connection
	channel *amqp.Channel
}

func NewRMQMessenger(config RabbitMQConfig) (*RMQMessenger, error) {
	log.Println("Initializing RabbitMQ messenger...")

	var conn *amqp.Connection
	var err error

	RMQUrl := fmt.Sprintf(
		"amqp://%s:%s@%s:%s/",
		config.User,
		config.Password,
		config.Host,
		config.Port,
	)

	for attempt := 1; attempt <= maxRetries; attempt++ {
		log.Printf(
			"Attempting to connect to RabbitMQ, attempt %d/%d\n", attempt, maxRetries,
		)
		conn, err = amqp.Dial(RMQUrl)
		if err == nil {
			log.Println("RabbitMQ connection established")
			break
		}

		log.Printf("Failed to connect to RabbitMQ: %v\n", err)
		if attempt < maxRetries {
			log.Printf("Retrying in %v...\n", retryDelay)
			time.Sleep(retryDelay)
		} else {
			return nil, fmt.Errorf(
				"failed to connect to RabbitMQ after %d attempts: %w", maxRetries, err,
			)
		}
	}

	channel, err := conn.Channel()

	if err != nil {
		return nil, fmt.Errorf("failed to open a channel: %w", err)
	}

	return &RMQMessenger{
		conn:    conn,
		channel: channel,
	}, nil
}

func (r *RMQMessenger) PublishUserCreated(u *CreateUserPublish) error {
	log.Printf("Publishing user created event for user: %s\n", u.Username)

	err := declareQueue(r.channel, "new_user_queue")
	if err != nil {
		return fmt.Errorf("failed to declare a queue: %w", err)
	}

	// serialize the CreateUserRequest to JSON
	userData, err := json.Marshal(u)
	if err != nil {
		return fmt.Errorf("failed to serialize user data: %w", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	err = r.channel.PublishWithContext(
		ctx,
		"",               // exchange
		"new_user_queue", // routing key (queue name)
		false,            // mandatory
		false,            // immediate
		amqp.Publishing{
			DeliveryMode: amqp.Persistent,
			ContentType:  "application/json",
			Body:         userData,
		},
	)
	if err != nil {
		return fmt.Errorf("failed to publish a message: %w", err)
	}

	log.Printf("User created event published for user: %s\n", u.Username)

	return nil
}

func (r *RMQMessenger) SubscribeUserCreatedError(writeStore WriteStorage) error {
	log.Println("Subscribing to user created error events...")

	err := declareQueue(r.channel, "new_user_error_queue")
	if err != nil {
		return fmt.Errorf("failed to declare a queue: %w", err)
	}

	msgs, err := r.channel.Consume(
		"new_user_error_queue", // queue
		"",                     // consumer
		true,                   // auto-ack
		false,                  // exclusive
		false,                  // no-local
		false,                  // no-wait
		nil,                    // args
	)
	if err != nil {
		return fmt.Errorf("failed to register a consumer: %w", err)
	}

	go func() {
		for msg := range msgs {
			var user CreateUserPublish
			err := json.Unmarshal(msg.Body, &user)
			if err != nil {
				log.Printf("Failed to unmarshal user created event: %v\n", err)
				continue
			}
			writeStore.HardDeleteUser(user.ID)
		}
	}()
	log.Printf("finished subscribing to user created error events\n")

	return nil
}

func declareQueue(ch *amqp.Channel, name string) error {
	_, err := ch.QueueDeclare(
		name,  // name of the queue
		true,  // durable
		false, // delete when unused
		false, // exclusive
		false, // no-wait
		nil,   // arguments
	)
	if err != nil {
		return fmt.Errorf("failed to declare a queue: %w", err)
	}

	return nil
}
