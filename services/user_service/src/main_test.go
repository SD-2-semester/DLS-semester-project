package main

import (
	"os"
	"testing"
)

func TestMain(m *testing.M) {

	a := App{}
	a.Initialize(
		os.Getenv("APP_DB_USERNAME"),
		os.Getenv("APP_DB_PASSWORD"),
		os.Getenv("APP_DB_NAME"),
	)
}
