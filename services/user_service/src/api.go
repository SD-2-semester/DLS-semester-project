package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

type APIServer struct {
	listenAddr string
	store      Storage
}

func NewAPIServer(listenAddr string, store Storage) *APIServer {
	return &APIServer{listenAddr: listenAddr, store: store}
}

func (s *APIServer) Run() {
	router := mux.NewRouter()

	router.HandleFunc("/users", makeHTTPHandleFunc(s.handleUser))
	router.HandleFunc("/users/{id}", withJWTAuth(makeHTTPHandleFunc(s.handleGetUserByID)))
	router.HandleFunc("/auth/login-email", makeHTTPHandleFunc(s.handleLoginEmail))

	log.Println("Starting server on", s.listenAddr)

	http.ListenAndServe(s.listenAddr, router)
}

func (s *APIServer) handleUser(w http.ResponseWriter, r *http.Request) error {
	if r.Method == "GET" {
		return s.handleGetUsers(w, r)
	}

	if r.Method == "POST" {
		return s.handleCreateUser(w, r)
	}

	return fmt.Errorf("unsupported method %s", r.Method)
}

func (s *APIServer) handleGetUsers(w http.ResponseWriter, r *http.Request) error {
	users, err := s.store.GetUsers()

	if err != nil {
		return err
	}

	return WriteJSON(w, http.StatusOK, users)
}

func (s *APIServer) handleGetUserByID(w http.ResponseWriter, r *http.Request) error {
	if r.Method == "GET" {
		uid, err := getID(r)

		if err != nil {
			return err
		}

		user, err := s.store.GetUserByID(uid)

		if err != nil {
			return err
		}

		return WriteJSON(w, http.StatusOK, user)
	}

	if r.Method == "DELETE" {
		log.Println("deleting user")

		return nil
	}

	return fmt.Errorf("unsupported method %s", r.Method)
}

func (s *APIServer) handleCreateUser(w http.ResponseWriter, r *http.Request) error {
	createUserReq := new(CreateUserRequest)

	if err := json.NewDecoder(r.Body).Decode(createUserReq); err != nil {
		return err
	}

	user := NewUser(
		createUserReq.Username,
		createUserReq.Email,
		createUserReq.Password,
	)

	if err := s.store.CreateUser(user); err != nil {
		return err
	}

	return WriteJSON(w, http.StatusCreated, user)

}

func (s *APIServer) handleDeleteUser(w http.ResponseWriter, r *http.Request) error {
	uid, err := getID(r)

	if err != nil {
		return err
	}

	log.Println("deleting user", uid)

	return nil
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

	if user.Password != loginReq.Password {
		return fmt.Errorf("invalid password")
	}

	token, err := createJWT(user)

	if err != nil {
		return err
	}

	return WriteJSON(w, http.StatusOK, map[string]string{"access_token": token})

}

func WriteJSON(w http.ResponseWriter, status int, v any) error {
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(status)
	return json.NewEncoder(w).Encode(v)
}

func createJWT(user *User) (string, error) {
	claims := &jwt.MapClaims{
		"user_id": user.ID.String(),
		"exp":     time.Now().Add(time.Minute * 30).Unix(),
	}

	secret := os.Getenv("JWT_SECRET")
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	ss, err := token.SignedString([]byte(os.Getenv(secret)))

	fmt.Printf("token: %s\n", ss)

	return ss, err
}

func withJWTAuth(handlerFunc http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		log.Println("withJWTAuth")

		tokenString := r.Header.Get("Authorization")
		_, err := validateJWT(tokenString)

		if err != nil {
			WriteJSON(
				w,
				http.StatusUnauthorized,
				ApiError{Error: "invalid token"},
			)
			return
		}

		handlerFunc(w, r)
	}
}

func validateJWT(tokenString string) (*jwt.Token, error) {
	secret := os.Getenv("JWT_SECRET")
	return jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}

		return []byte(secret), nil
	})

}

type apiFunc func(w http.ResponseWriter, r *http.Request) error

type ApiError struct {
	Error string `json:"error"`
}

func makeHTTPHandleFunc(f apiFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if err := f(w, r); err != nil {
			WriteJSON(w, http.StatusBadRequest, ApiError{Error: err.Error()})

		}
	}
}

func getID(r *http.Request) (uuid.UUID, error) {
	id := mux.Vars(r)["id"]
	uid, err := uuid.Parse(id)

	if err != nil {
		return uuid.Nil, fmt.Errorf("invalid user id %s", id)
	}

	return uid, nil
}
