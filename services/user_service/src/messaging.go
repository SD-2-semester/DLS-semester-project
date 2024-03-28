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
	rabbitMQURL = "amqp://user:password@rabbitmq:5672/"
	queueName   = "new_user_queue"
	maxRetries  = 20
	retryDelay  = 2 * time.Second
)

type Publisher interface {
	PublishUserCreated(u *CreateUserPublish) error
}

type RabbitMQPublisher struct {
	conn    *amqp.Connection
	channel *amqp.Channel
}

func NewRabbitMQPublisher() (*RabbitMQPublisher, error) {
	log.Println("Initializing RabbitMQ publisher...")

	var conn *amqp.Connection
	var err error

	for attempt := 1; attempt <= maxRetries; attempt++ {
		log.Printf(
			"Attempting to connect to RabbitMQ, attempt %d/%d\n", attempt, maxRetries,
		)
		conn, err = amqp.Dial(rabbitMQURL)
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

	_, err = channel.QueueDeclare(
		queueName, // name of the queue
		true,      // durable
		false,     // delete when unused
		false,     // exclusive
		false,     // no-wait
		nil,       // arguments
	)
	if err != nil {
		return nil, fmt.Errorf("failed to declare a queue: %w", err)
	}

	return &RabbitMQPublisher{
		conn:    conn,
		channel: channel,
	}, nil
}

func (r *RabbitMQPublisher) PublishUserCreated(u *CreateUserPublish) error {
	log.Printf("Publishing user created event for user: %s\n", u.Username)
	if r.channel == nil {
		return fmt.Errorf("RabbitMQ channel not initialized")
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
		"",        // exchange
		queueName, // routing key (queue name)
		false,     // mandatory
		false,     // immediate
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
