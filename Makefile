venv:
	uv sync
	@echo "\n✅ Dependencies installed. Run 'source .venv/bin/activate' to activate the virtual environment."

env:
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	@echo "\n✅ Environment variables setup!"

init-backend:
	set -e
	@echo "🚀 Initializing backend infrastructure services..."
	docker compose --file backend/compose.yaml up -d langfuse-minio
	@echo "⌛ Waiting for MinIO to be ready on http://localhost:13308/minio/health/ready ..."
	@until curl -sf http://localhost:13308/minio/health/ready > /dev/null; do \
		sleep 2; \
	done
	@echo "✅ MinIO is ready, running init job..."
	docker compose --file backend/compose.yaml --profile init build langfuse-minio-init
	docker compose --file backend/compose.yaml --profile init run --rm langfuse-minio-init
	docker compose --file backend/compose.yaml up -d --build
	@echo "\n✅ Backend infrastructure ready!"
	@echo "Agno: create your free account at https://os.agno.com and connect your local agents - http://localhost:13300"
	@echo "Langfuse available at http://localhost:13303/ with email: admin@email.com and password: admin123"
	@echo "No need to setup Langfuse thanks to Headless Initialization - https://langfuse.com/self-hosting/administration/headless-initialization"

init-frontend:
	set -e
	@echo "🚀 Initializing frontend infrastructure services..."
	docker compose --file frontend/compose.yaml up -d chainlit-postgres chainlit-minio
	@echo "\n⌛ Waiting for Chainlit Postgres to be ready ..."
	@until docker exec chainlit-postgres pg_isready -U "$$POSTGRES_USER" > /dev/null 2>&1; do \
		sleep 2; \
	done
	@echo "\n⌛ Waiting for Chainlit MinIO to be ready on http://localhost:13203/minio/health/ready ..."
	@until curl -sf http://localhost:13203/minio/health/ready > /dev/null; do \
		sleep 2; \
	done
	@echo "\n✅ DB & MinIO are ready, running init jobs..."
	docker compose --file frontend/compose.yaml --profile init build chainlit-db-init chainlit-minio-init
	docker compose --file frontend/compose.yaml --profile init run --rm chainlit-db-init
	docker compose --file frontend/compose.yaml --profile init run --rm chainlit-minio-init
	@echo "\n🚀 Starting remaining frontend services..."
	docker compose --file frontend/compose.yaml up -d --build
	@echo "\n✅ Frontend infrastructure ready!"
	@echo "Chainlit available at http://localhost:13201/ with username: admin and password: admin"
	@echo "For dev environment run: uv run --package chainlit-app --directory frontend chainlit run app.py -w --port 13200"
	@echo "Chainlit dev environment at http://localhost:13200/"

backend-down:
	@echo "Stopping backend services..."
	docker compose --file backend/compose.yaml down --remove-orphans
	@echo "\n✅ Backend services down!"

frontend-down:
	@echo "Stopping frontend services..."
	docker compose --file frontend/compose.yaml down --remove-orphans
	@echo "\n✅ Frontend services down!"

# Start Chainlit dev mode
chainlit-dev:
	uv run --package chainlit-app --directory frontend chainlit run app.py -w --port 13200

# Deploy Chainlit
chainlit-deploy:
	docker compose --file frontend/compose.yaml build chainlit-app
	docker compose --file frontend/compose.yaml up chainlit-app -d --force-recreate
	@echo "\n✅ Chainlit docker image built and deployed at http://localhost:13201/"

# Start all services
up:
	docker compose --file backend/compose.yaml up
	docker compose --file frontend/compose.yaml up
	@echo "\nServices running:"
	@echo "- Agno AgentOS: http://localhost:13300"
	@echo "- API Documentation: http://localhost:13300/docs"
	@echo "- Langfuse: http://localhost:13303"
	@echo "- Chainlit: http://localhost:13201"

# Stop all services
down:
	docker compose --file backend/compose.yaml down --remove-orphans
	docker compose --file frontend/compose.yaml down --remove-orphans
	@echo "\nAll services down"

# Clean everything (volumes included)
clean:
	docker compose --file frontend/compose.yaml --profile init down
	docker compose --file frontend/compose.yaml --profile init down --volumes --remove-orphans
	docker compose --file backend/compose.yaml --profile init down
	docker compose --file backend/compose.yaml down --volumes --remove-orphans
	@echo "\n🧹 All containers and volumes removed"