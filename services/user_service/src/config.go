package main

import "os"

type DBConfig struct {
	Host     string
	User     string
	DBName   string
	Password string
	Port     string
}

type RabbitMQConfig struct {
	Host     string
	Port     string
	User     string
	Password string
}

func LoadDBConfig(prefix string) DBConfig {
	return DBConfig{
		Host:     os.Getenv(prefix + "DB_HOST"),
		User:     os.Getenv(prefix + "DB_USER"),
		DBName:   os.Getenv(prefix + "DB_NAME"),
		Password: os.Getenv(prefix + "DB_PASSWORD"),
		Port:     os.Getenv(prefix + "DB_PORT"),
	}
}

func LoadRabbitMQConfig() RabbitMQConfig {
	return RabbitMQConfig{
		Host:     os.Getenv("AUTHSERVICE_RABBITMQ_HOST"),
		Port:     os.Getenv("AUTHSERVICE_RABBITMQ_PORT"),
		User:     os.Getenv("AUTHSERVICE_RABBITMQ_USER"),
		Password: os.Getenv("AUTHSERVICE_RABBITMQ_PASSWORD"),
	}
}
