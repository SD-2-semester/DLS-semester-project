package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	"github.com/google/uuid"
	_ "github.com/lib/pq"
)

type Storage interface {
	CreateUser(*User) error
	GetUsers() ([]*User, error)
	GetUserByID(id uuid.UUID) (*User, error)
	GetUserByEmail(email string) (*User, error)
}

type PostgresStore struct {
	db *sql.DB
}

func NewPostgresStore() (*PostgresStore, error) {
	host := os.Getenv("AUTHSERVICE_DB_HOST")
	user := os.Getenv("AUTHSERVICE_DB_USER")
	dbname := os.Getenv("AUTHSERVICE_DB_NAME")
	password := os.Getenv("AUTHSERVICE_DB_PASSWORD")
	port := os.Getenv("AUTHSERVICE_DB_PORT")

	// Connection string
	psqlInfo := fmt.Sprintf("host=%s port=%s user=%s "+
		"password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	log.Println(psqlInfo)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		return nil, err
	}

	if err := db.Ping(); err != nil {
		return nil, err
	}

	return &PostgresStore{db: db}, nil
}

func (s *PostgresStore) Init() error {
	return s.createUserTable()
}

func (s *PostgresStore) createUserTable() error {
	query := `
		CREATE TABLE IF NOT EXISTS users (
			id UUID PRIMARY KEY,
			username VARCHAR(50) UNIQUE,
			email VARCHAR(255) UNIQUE,
			password VARCHAR(255),
			created_at TIMESTAMP
		)
	`

	_, err := s.db.Exec(query)
	return err
}

func (s *PostgresStore) CreateUser(u *User) error {
	query := `
		INSERT INTO users (id, username, email, password, created_at)
		VALUES ($1, $2, $3, $4, $5)
	`

	_, err := s.db.Exec(query, u.ID, u.Username, u.Email, u.Password, u.CreatedAt)
	return err
}

func (s *PostgresStore) GetUsers() ([]*User, error) {
	query := `
		SELECT id, username, email, created_at
		FROM users
	`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}

	users := []*User{}

	for rows.Next() {
		user, err := scanIntoUser(rows)
		if err != nil {
			return nil, err
		}

		users = append(users, user)
	}

	return users, nil
}

func (s *PostgresStore) GetUserByID(id uuid.UUID) (*User, error) {
	query := `
		SELECT id, username, email, created_at
		FROM users
		WHERE id = $1
	`

	rows, err := s.db.Query(query, id)
	if err != nil {
		return nil, err
	}

	for rows.Next() {
		return scanIntoUser(rows)
	}

	return nil, fmt.Errorf("user %d not found", id)
}

func (s *PostgresStore) GetUserByEmail(email string) (*User, error) {
	query := `
		SELECT *
		FROM users
		WHERE email = $1
	`

	row := s.db.QueryRow(query, email)

	user := new(User)

	err := row.Scan(
		&user.ID,
		&user.Username,
		&user.Email,
		&user.Password,
		&user.CreatedAt,
	)

	if err == nil {
		return user, nil
	}

	return nil, fmt.Errorf("user %s not found", email)
}

func scanIntoUser(rows *sql.Rows) (*User, error) {
	user := new(User)

	err := rows.Scan(
		&user.ID,
		&user.Username,
		&user.Email,
		&user.CreatedAt,
	)

	return user, err
}
