# Use the official Golang image to create a build artifact.
# This is stage 'builder'.
FROM golang:1.22 AS builder

WORKDIR /app

# Copy go.mod and go.sum files and download modules.
COPY src/go.mod src/go.sum ./
RUN go mod download

# Copy the source code.
COPY src/ ./

# Build the application.
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# This is the final stage where the compiled application 'main' will be run.
FROM alpine

WORKDIR /app

# Copy the pre-built binary from the previous stage.
COPY --from=builder /app/main .

# Command to run the executable
CMD ["./main"]
