build:
	@go build -o bin/user_service

run: build
	@./bin/user_service

test:
	@go test -v ./...

lint:
	@goimports -l -w .
	@golangci-lint run

fmt:
	@go fmt ./...