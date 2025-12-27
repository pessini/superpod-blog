init:
	@echo "🚀 Initializing infrastructure services..."
	docker compose --profile init up -d --build
	docker compose wait chainlit-db-init chainlit-minio-init
	docker compose rm -f chainlit-db-init chainlit-minio-init
	@echo "✅ Infrastructure ready!"
	@echo "For dev environment run: chainlit run app.py"
	@echo "For docker environment run: docker compose chainlit-app up -d"

deploy:
	docker compose up chainlit-app -d --build
	@echo "✅ Docker environment ready at http://localhost:13201"

# Start all services
up:
	docker compose up -d

# Stop all services
down:
	docker compose down

# Clean everything (volumes included)
clean:
	docker compose down -v
	@echo "🧹 All containers and volumes removed"