package main

import (
	"log"
	"net/http"
)

func LogMiddleware(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("Request: %s %s\n", r.Method, r.URL.Path)
		h.ServeHTTP(w, r)
	})
}
