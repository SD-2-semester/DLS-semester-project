package main

import (
	"github.com/google/uuid"
)

type User struct {
	ID       uuid.UUID `json:"id"`
	Username string    `json:"username"`
	Email    string    `json:"email"`
	Password string    `json:"password"`
}

func NewUser(username, email, password string) *User {
	return &User{
		ID:       uuid.New(),
		Username: username,
		Email:    email,
		Password: password,
	}
}
