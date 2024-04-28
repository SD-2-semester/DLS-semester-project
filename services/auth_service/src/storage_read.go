package main

import (
	"database/sql"
	"fmt"
	"log"

	"github.com/google/uuid"
	_ "github.com/lib/pq"
)

type ReadStorage interface {
	GetUsers() ([]*User, error)
	GetUserByID(id uuid.UUID) (*User, error)
	GetUserByEmail(email string) (*User, error)
}

type PostgresStoreRead struct {
	db *sql.DB
}

func NewPostgresStoreRead(config DBConfig) (*PostgresStoreRead, error) {
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

	return &PostgresStoreRead{db: db}, nil
}

func (s *PostgresStoreRead) Init() error {
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
		CREATE INDEX IF NOT EXISTS email_idx
		ON users (email)
	`

	_, err = s.db.Exec(query)

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

func (s *PostgresStoreRead) GetUsers() ([]*User, error) {
	query := `
		SELECT u.id, u.username, u.email, u.created_at
		FROM users u
		LEFT JOIN user_deletes ud ON u.id = ud.id
		WHERE ud.id IS NULL
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

func (s *PostgresStoreRead) GetUserByID(id uuid.UUID) (*User, error) {
	query := `
		SELECT u.id, u.username, u.email, u.created_at
		FROM users u
		LEFT JOIN user_deletes ud ON u.id = ud.id
		WHERE ud.id IS NULL AND u.id = $1
	`

	rows, err := s.db.Query(query, id)
	if err != nil {
		return nil, err
	}

	for rows.Next() {
		return scanIntoUser(rows)
	}

	return nil, fmt.Errorf("user %s not found", id)
}

func (s *PostgresStoreRead) GetUserByEmail(email string) (*User, error) {
	query := `
		SELECT u.id, u.username, u.email, u.password, u.created_at
		FROM users u
		LEFT JOIN user_deletes ud ON u.id = ud.id
		WHERE ud.id IS NULL AND u.email = $1
	`

	row := s.db.QueryRow(query, email)
	log.Println(row)

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
