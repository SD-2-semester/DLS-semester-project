package main

import "os"

type DBConfig struct {
	Host     string
	User     string
	DBName   string
	Password string
	Port     string
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
