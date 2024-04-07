package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

func createJWT(user *User) (string, error) {
	claims := &jwt.MapClaims{
		"user_id": user.ID.String(),
		"exp":     time.Now().Add(time.Minute * 30).Unix(),
	}

	secret := os.Getenv("JWT_SECRET")
	if secret == "" {
		secret = "my_secret"
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	ss, err := token.SignedString([]byte(os.Getenv(secret)))

	fmt.Printf("token: %s\n", ss)

	return ss, err
}

// func withJWTAuth(handlerFunc http.HandlerFunc, store Storage) http.HandlerFunc {
// 	return func(w http.ResponseWriter, r *http.Request) {
// 		log.Println("withJWTAuth")

// 		tokenString := r.Header.Get("Authorization")
// 		token, err := validateJWT(tokenString)

// 		if err != nil {
// 			permissionDenied(w)
// 			return
// 		}

// 		if !token.Valid {
// 			permissionDenied(w)
// 			return
// 		}

// 		handlerFunc(w, r)
// 	}
// }

func validateJWT(tokenString string) (*jwt.Token, error) {
	secret := os.Getenv("JWT_SECRET")
	return jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}

		return []byte(secret), nil
	})
}

func currentUserFromJWT(r *http.Request, store ReadStorage) (*User, error) {
	tokenString := r.Header.Get("Authorization")

	if tokenString == "" {
		return nil, fmt.Errorf("missing token")
	}

	log.Println("tokenString: ", tokenString)

	token, err := validateJWT(tokenString)
	if err != nil {
		return nil, err
	}

	if !token.Valid {
		return nil, fmt.Errorf("invalid token")
	}

	uid := token.Claims.(jwt.MapClaims)["user_id"].(string)

	return store.GetUserByID(uuid.MustParse(uid))
}

func hashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}

func checkPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}
