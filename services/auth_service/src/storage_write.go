package main

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/google/uuid"
)

type WriteStorage interface {
	CreateUser(*User) error
	DeleteUser(uuid.UUID) error
}

type PostgresStoreWrite struct {
	db *sql.DB
}

func NewPostgresStoreWrite(config DBConfig) (*PostgresStoreWrite, error) {
	psqlInfo := fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		config.Host, config.Port, config.User, config.Password, config.DBName,
	)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		return nil, err
	}

	if err := db.Ping(); err != nil {
		return nil, err
	}

	return &PostgresStoreWrite{db: db}, nil
}

func (s *PostgresStoreWrite) Init() error {
	query := `
		CREATE TABLE IF NOT EXISTS users (
			id UUID PRIMARY KEY,
			username VARCHAR(50),
			email VARCHAR(255) UNIQUE,
			password VARCHAR(255),
			created_at TIMESTAMP
		)
	`

	_, err := s.db.Exec(query)

	if err != nil {
		return err
	}

	query = `
		CREATE TABLE IF NOT EXISTS user_deletes (
			id UUID PRIMARY KEY,
			created_at TIMESTAMP
		)
	`

	_, err = s.db.Exec(query)
	return err
}

func (s *PostgresStoreWrite) CreateUser(u *User) error {
	query := `
		INSERT INTO users (id, username, email, password, created_at)
		VALUES ($1, $2, $3, $4, $5)
	`

	_, err := s.db.Exec(query, u.ID, u.Username, u.Email, u.Password, u.CreatedAt)
	return err
}

func (s *PostgresStoreWrite) DeleteUser(id uuid.UUID) error {
	query := `
		INSERT INTO user_deletes (id, created_at)
		VALUES ($1, $2)
	`

	_, err := s.db.Exec(query, id, time.Now().UTC())
	return err
}
