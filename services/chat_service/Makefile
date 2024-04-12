run: ## Run the project
	docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build


lint: ## Lint
	poetry run black chat_service
	poetry run ruff check . --fix
	poetry run mypy chat_service