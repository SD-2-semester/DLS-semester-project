FROM golang:1.21

WORKDIR /app

COPY src/go.mod src/go.sum ./
RUN go mod download

COPY src/*.go ./

RUN CGO_ENABLED=0 GOOS=linux go build -o /docker-gs-ping

# Document the port the application listens on
EXPOSE 8080
CMD ["/docker-gs-ping"]
