# 🧊 Cube.com

**Cube.com** is a full-stack Rubik's Cube learning and practice platform built with a microservice architecture. Users can learn solving methods, practice with a 3D interactive cube, track solve times, and compete with others.

---

## 📐 Architecture Overview

```
                    ┌──────────────┐
                    │   Frontend   │  React + Three.js
                    │  (Port 3001) │  3D Cube, Timer, Lessons
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Nginx Gateway│  Reverse Proxy
                    │  (Port 8080) │  API Routing & CORS
                    └──┬───┬───┬───┘
                       │   │   │
          ┌────────────┘   │   └────────────┐
          ▼                ▼                ▼
   ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
   │ User Service │ │  Learning   │ │   Session    │
   │  (Port 8001) │ │  Service    │ │   Service    │
   │   FastAPI    │ │ (Port 8002) │ │  (Port 8003) │
   └──────┬───────┘ └──────┬──────┘ └──────┬───────┘
          │                │               │
          ▼                ▼               ▼
   ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
   │ PostgreSQL  │ │   MongoDB   │ │    Redis     │
   │  (Port 5432)│ │ (Port 27017)│ │  (Port 6379) │
   └─────────────┘ └─────────────┘ └──────────────┘
```

## 🏗️ Services

| Service            | Tech Stack         | Port | Description                                  |
| ------------------ | ------------------ | ---- | -------------------------------------------- |
| **Frontend**       | React, Three.js    | 3001 / 8080 | 3D cube visualization, timer, lesson viewer  |
| **User Service**   | FastAPI, PostgreSQL | 8001 | Authentication, profiles, stats              |
| **Learning Service** | FastAPI, MongoDB  | 8002 | Lessons, algorithms, scramble generation     |
| **Session Service** | FastAPI, Redis     | 8003 | Solve sessions, timer, history tracking      |
| **API Gateway**    | Nginx              | 8080 | Reverse proxy, CORS, routing                 |

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Make](https://www.gnu.org/software/make/) (optional, for convenience commands)

### 1. Clone and configure

```bash
git clone https://github.com/your-org/cube.git
cd cube
cp .env.example .env
# Edit .env with your settings (especially secrets for production)
```

### 2. Start in development mode

```bash
# Using Make
make up-dev

# Or using Docker Compose directly
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 3. Access the application

- **App**: http://localhost:8080
- **API Gateway**: http://localhost:8080/api
- **User Service (direct)**: http://localhost:8001/docs
- **Learning Service (direct)**: http://localhost:8002/docs
- **Session Service (direct)**: http://localhost:8003/docs

## 🛠️ Development Commands

```bash
make help          # Show all available commands
make up-dev        # Start with hot-reload
make down          # Stop all services
make logs          # Follow service logs
make ps            # Show running services
make test          # Run all tests
make lint          # Run linting
make clean         # Clean up everything
```

## 🧪 Testing

```bash
make test              # Run all service tests
make test-user         # Test user-service only
make test-learning     # Test learning-service only
make test-session      # Test session-service only
```

## 🚢 Deployment

### Docker Hub

```bash
make build             # Build all images
make push-all          # Push to Docker Hub (set REGISTRY env var)
```

### Kubernetes

```bash
make minikube-setup    # Setup local Minikube cluster
make k8s-deploy        # Deploy all manifests
make k8s-delete        # Tear down deployment
```

## 📁 Project Structure

```
cube/
├── frontend/               # React SPA with 3D cube
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route pages
│   │   ├── services/       # API client services
│   │   └── types/          # TypeScript interfaces
│   ├── Dockerfile          # Production build
│   └── Dockerfile.dev      # Development with hot-reload
├── services/
│   ├── user-service/       # Auth & user management
│   ├── learning-service/   # Lessons & algorithms
│   └── session-service/    # Solve sessions & timer
├── gateway/                # Nginx reverse proxy config
├── k8s/                    # Kubernetes manifests
├── docker-compose.yml      # Production compose
├── docker-compose.dev.yml  # Development overrides
├── Makefile                # Convenience commands
└── .env.example            # Environment template
```

## 📄 License

MIT © Cube.com Team
