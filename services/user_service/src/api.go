package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	"github.com/gorilla/mux"
)

type APIServer struct {
	listenAddr string
	store      Storage
}

func NewAPIServer(listenAddr string, store Storage) *APIServer {
	return &APIServer{listenAddr: listenAddr, store: store}
}

// Run starts the API server
func (s *APIServer) Run() {
	router := mux.NewRouter()

	server := &http.Server{
		Addr:         s.listenAddr,
		Handler:      router,
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	s.setupRoutes(router)

	go func() {
		log.Printf("Server started on %s\n", s.listenAddr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("ListenAndServe error: %v", err)
		}
	}()

	shutdownGracefully(server)
}

func (s *APIServer) setupRoutes(router *mux.Router) {
	// health check
	router.HandleFunc(
		"/health", s.logRequest(makeHTTPHandleFunc(s.handleHealthCheck)),
	).Methods(http.MethodGet)

	// user endpoints
	router.HandleFunc(
		"/users", s.logRequest(makeHTTPHandleFunc(s.handleGetUsers)),
	).Methods(http.MethodGet)

	router.HandleFunc(
		"/users/me", s.logRequest(makeHTTPHandleFunc(s.handleGetCurrentUser)),
	).Methods(http.MethodGet)

	// auth endpoints
	router.HandleFunc(
		"/auth/login-email", s.logRequest(makeHTTPHandleFunc(s.handleLoginEmail)),
	).Methods(http.MethodPost)

	router.HandleFunc(
		"/auth/register", s.logRequest(makeHTTPHandleFunc(s.handleRegisterUser)),
	).Methods(http.MethodPost)

	// default handler for unmatched routes
	router.PathPrefix("/").HandlerFunc(s.logUnmatchedRequest)
}

func (s *APIServer) logRequest(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		log.Printf("Request: %s %s\n", r.Method, r.URL.Path)
		next(w, r)
	}
}

func (s *APIServer) logUnmatchedRequest(w http.ResponseWriter, r *http.Request) {
	log.Printf("Unhandled request: %s %s\n", r.Method, r.URL.Path)
	w.WriteHeader(http.StatusNotFound)
}

func shutdownGracefully(server *http.Server) {
	stopChan := make(chan os.Signal, 1)
	signal.Notify(stopChan, os.Interrupt)

	<-stopChan // wait for interrupt signal

	// create a deadline to wait for.
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	log.Println("Shutting down server...")
	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server Shutdown Failed:%+v", err)
	}
	log.Println("Server gracefully stopped.")
}

func (s *APIServer) handleGetUsers(w http.ResponseWriter, _ *http.Request) error {
	users, err := s.store.GetUsers()
	if err != nil {
		return err
	}

	return WriteJSON(w, http.StatusOK, users)
}

func (s *APIServer) handleRegisterUser(w http.ResponseWriter, r *http.Request) error {
	createUserReq := new(CreateUserRequest)

	if err := json.NewDecoder(r.Body).Decode(createUserReq); err != nil {
		return err
	}

	hashedPassword, err := hashPassword(createUserReq.Password)
	if err != nil {
		return err
	}

	user := NewUser(
		createUserReq.Username,
		createUserReq.Email,
		hashedPassword,
	)

	if err := s.store.CreateUser(user); err != nil {
		return err
	}

	return WriteJSON(w, http.StatusCreated, user)
}

func (s *APIServer) handleLoginEmail(w http.ResponseWriter, r *http.Request) error {
	if r.Method != "POST" {
		return fmt.Errorf("unsupported method %s", r.Method)
	}

	loginReq := new(LoginEmailRequest)

	if err := json.NewDecoder(r.Body).Decode(loginReq); err != nil {
		return err
	}

	user, err := s.store.GetUserByEmail(loginReq.Email)
	if err != nil {
		return err
	}

	if !checkPasswordHash(loginReq.Password, user.Password) {
		return fmt.Errorf("invalid email or password")
	}

	token, err := createJWT(user)
	if err != nil {
		return err
	}

	return WriteJSON(w, http.StatusOK, map[string]string{"access_token": token})
}

func (s *APIServer) handleHealthCheck(w http.ResponseWriter, _ *http.Request) error {
	return WriteJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

func (s *APIServer) handleGetCurrentUser(w http.ResponseWriter, r *http.Request) error {
	user, err := currentUserFromJWT(r, s.store)
	if err != nil {
		return err
	}

	return WriteJSON(w, http.StatusOK, user)
}

func WriteJSON(w http.ResponseWriter, status int, v any) error {
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(status)
	return json.NewEncoder(w).Encode(v)
}

func makeHTTPHandleFunc(f APIFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if err := f(w, r); err != nil {
			err := WriteJSON(w, http.StatusBadRequest, APIError{Error: err.Error()})
			if err != nil {
				log.Printf("failed to write error response: %v", err)
			}
		}
	}
}