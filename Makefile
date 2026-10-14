# ============================================================
# Cube.com - Makefile
# Convenience targets for building, running, testing, and
# deploying the Cube.com microservice platform.
# ============================================================

.DEFAULT_GOAL := help
COMPOSE := docker compose
COMPOSE_DEV := $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml
K8S_DIR := k8s

# Registry settings (override via env or CLI: make push-all REGISTRY=myrepo)
REGISTRY ?= cubecom
TAG ?= latest

.PHONY: help build up up-dev down logs ps \
        build-user build-learning build-session build-frontend \
        push-all k8s-deploy k8s-delete minikube-setup \
        test test-user test-learning test-session lint clean

# ----------------------------------------------------------
# Help - Display all available targets
# ----------------------------------------------------------
help: ## Show this help message
	@echo.
	@echo  Cube.com - Available Commands
	@echo  ==============================
	@echo.
	@echo  BUILD
	@echo    make build            - Build all Docker images
	@echo    make build-user       - Build user-service image
	@echo    make build-learning   - Build learning-service image
	@echo    make build-session    - Build session-service image
	@echo    make build-frontend   - Build frontend image
	@echo.
	@echo  RUN
	@echo    make up               - Start all services (production mode)
	@echo    make up-dev           - Start all services (development mode with hot-reload)
	@echo    make down             - Stop all services
	@echo    make logs             - Follow logs for all services
	@echo    make ps               - Show running services
	@echo.
	@echo  TEST
	@echo    make test             - Run all tests
	@echo    make test-user        - Run user-service tests
	@echo    make test-learning    - Run learning-service tests
	@echo    make test-session     - Run session-service tests
	@echo    make lint             - Run linting on all services
	@echo.
	@echo  DEPLOY
	@echo    make push-all         - Push all images to Docker Hub
	@echo    make k8s-deploy       - Deploy to Kubernetes
	@echo    make k8s-delete       - Delete Kubernetes resources
	@echo    make minikube-setup   - Setup Minikube environment
	@echo.
	@echo  MISC
	@echo    make clean            - Clean up containers, volumes, and build artifacts
	@echo.

# ----------------------------------------------------------
# Build targets
# ----------------------------------------------------------
build: ## Build all Docker images
	$(COMPOSE) build

build-user: ## Build user-service image
	$(COMPOSE) build user-service

build-learning: ## Build learning-service image
	$(COMPOSE) build learning-service

build-session: ## Build session-service image
	$(COMPOSE) build session-service

build-frontend: ## Build frontend image
	$(COMPOSE) build frontend

# ----------------------------------------------------------
# Run targets
# ----------------------------------------------------------
up: ## Start all services in production mode
	$(COMPOSE) up -d
	@echo "Cube.com is running at http://localhost:8080"

up-dev: ## Start all services in development mode with hot-reload
	$(COMPOSE_DEV) up -d
	@echo "Cube.com (dev) is running at http://localhost:8080"

up-user: ## Start only user-service + postgres (Objectif 10/20 - ultra léger en RAM)
	$(COMPOSE_DEV) up -d user-service postgres
	@echo "User Service is running at http://localhost:8001"

up-two-services: ## Start 2 services + gateway + DBs (Objectif 14/20)
	$(COMPOSE_DEV) up -d user-service postgres learning-service mongodb nginx-gateway
	@echo "Services running via Gateway at http://localhost:8080"

down: ## Stop all services and remove containers
	$(COMPOSE) down

logs: ## Follow logs for all services
	$(COMPOSE) logs -f

ps: ## Show status of running services
	$(COMPOSE) ps

# ----------------------------------------------------------
# Push targets
# ----------------------------------------------------------
push-all: ## Push all images to Docker Hub
	docker tag cube-frontend $(REGISTRY)/cube-frontend:$(TAG)
	docker tag cube-user-service $(REGISTRY)/cube-user-service:$(TAG)
	docker tag cube-learning-service $(REGISTRY)/cube-learning-service:$(TAG)
	docker tag cube-session-service $(REGISTRY)/cube-session-service:$(TAG)
	docker tag cube-gateway $(REGISTRY)/cube-gateway:$(TAG)
	docker push $(REGISTRY)/cube-frontend:$(TAG)
	docker push $(REGISTRY)/cube-user-service:$(TAG)
	docker push $(REGISTRY)/cube-learning-service:$(TAG)
	docker push $(REGISTRY)/cube-session-service:$(TAG)
	docker push $(REGISTRY)/cube-gateway:$(TAG)

# ----------------------------------------------------------
# Kubernetes targets
# ----------------------------------------------------------
k8s-deploy: ## Deploy all resources to Kubernetes
	kubectl apply -f $(K8S_DIR)/namespace.yaml
	kubectl apply -f $(K8S_DIR)/

k8s-delete: ## Delete all Kubernetes resources
	kubectl delete -f $(K8S_DIR)/ --ignore-not-found

minikube-setup: ## Setup Minikube for local Kubernetes development
	minikube start --cpus=4 --memory=8192 --driver=docker
	minikube addons enable ingress
	minikube addons enable metrics-server
	@echo "Minikube is ready. Run 'eval $$(minikube docker-env)' to use Minikube's Docker daemon."

# ----------------------------------------------------------
# Test targets
# ----------------------------------------------------------
test: test-user test-learning test-session ## Run all tests
	@echo "All tests passed!"

test-user: ## Run user-service tests
	$(COMPOSE) run --rm user-service pytest tests/ -v

test-learning: ## Run learning-service tests
	$(COMPOSE) run --rm learning-service pytest tests/ -v

test-session: ## Run session-service tests
	$(COMPOSE) run --rm session-service pytest tests/ -v

# ----------------------------------------------------------
# Lint target
# ----------------------------------------------------------
lint: ## Run linting on all Python services
	$(COMPOSE) run --rm user-service flake8 app/ --max-line-length=120
	$(COMPOSE) run --rm learning-service flake8 app/ --max-line-length=120
	$(COMPOSE) run --rm session-service flake8 app/ --max-line-length=120

# ----------------------------------------------------------
# Cleanup
# ----------------------------------------------------------
clean: ## Remove containers, volumes, and build artifacts
	$(COMPOSE) down -v --remove-orphans
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete."
