package main

import (
	"errors"
)

type User struct {
	ID       int    `json:"id"`
	Username string `json:"username"`
	Email    string `json:"email"`
	Password string `json:"password"`
}

func (u *User) createUser() error {
	return errors.New("not implemented")
}

func (u *User) getUser() error {
	return errors.New("not implemented")
}
