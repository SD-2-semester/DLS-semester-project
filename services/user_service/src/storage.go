package main

import (
	"database/sql"

	_ "github.com/lib/pq"

	"github.com/google/uuid"
)

type Storage interface {
	CreateUser(*User) error
	GetUser(uuid.UUID) (*User, error)
	DeleteUser(uuid.UUID) error
}

type PostgresStore struct {
	db *sql.DB
}

func NewPostgresStore() (*PostgresStore, error) {
	connStr := "user=postgres " +
		"dbname=postgres " +
		"password=mysecretpassword " +
		"sslmode=disable " +
		"port=5433"

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}

	if err := db.Ping(); err != nil {
		return nil, err
	}

	return &PostgresStore{db: db}, nil
}
