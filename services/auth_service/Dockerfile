FROM golang:1.22 AS builder

WORKDIR /app

COPY src/go.mod src/go.sum ./
RUN go mod download

COPY src/ ./

# Build the application for production.
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Dev
FROM builder AS dev

# Install 'air' for live reloading.
RUN go install github.com/cosmtrek/air@latest

CMD ["air", "-c", ".air.toml"]

# Prod
FROM debian:bullseye-slim

WORKDIR /app

# Copy the pre-built binary from the builder stage.
COPY --from=builder /app/main .

CMD ["./main"]
