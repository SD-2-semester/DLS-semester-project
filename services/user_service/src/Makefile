build:
	@go build -o bin/user_service

run-b: build
	@./bin/user_service

run:
	@docker-compose up

test:
	@go test -v ./...

lint:
	@goimports -l -w .
	@golangci-lint run

fmt:
	@go fmt ./...