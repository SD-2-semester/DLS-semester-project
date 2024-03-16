package main

import (
	"fmt"
	"net/http"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

func getID(r *http.Request) (uuid.UUID, error) {
	id := mux.Vars(r)["id"]
	uid, err := uuid.Parse(id)

	if err != nil {
		return uuid.Nil, fmt.Errorf("invalid user id %s", id)
	}

	return uid, nil
}
