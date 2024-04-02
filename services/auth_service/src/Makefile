build:
	@go build -o bin/auth_service

run-b: build
	@./bin/auth_service

run:
	@docker-compose up --build

test:
	@go test -v ./...

lint:
	@goimports -l -w .
	@golangci-lint run

fmt:
	@go fmt ./...

swag:
	@swag init -g api.go