# 📖 Cube.com — Guide d'Architecture Microservices

> **Document pédagogique complet** — Ce guide explique en profondeur chaque choix architectural,
> chaque technologie utilisée, et les concepts fondamentaux qui sous-tendent l'application Cube.com.

---

## Table des matières

1. [Introduction aux Microservices](#1-introduction-aux-microservices)
2. [Architecture globale de Cube.com](#2-architecture-globale-de-cubecom)
3. [Docker — Conteneurisation](#3-docker--conteneurisation)
4. [Kubernetes — Orchestration](#4-kubernetes--orchestration)
5. [FastAPI — Le framework backend](#5-fastapi--le-framework-backend)
6. [Communication inter-services : REST vs gRPC](#6-communication-inter-services--rest-vs-grpc)
7. [Bases de données — Le pattern Database-per-Service](#7-bases-de-données--le-pattern-database-per-service)
8. [API Gateway — Nginx Ingress](#8-api-gateway--nginx-ingress)
9. [Sécurité du cluster](#9-sécurité-du-cluster)
10. [React & Frontend](#10-react--frontend)
11. [DevOps — Docker Compose, Makefile & Scripts](#11-devops--docker-compose-makefile--scripts)
12. [Glossaire](#12-glossaire)

---

## 1. Introduction aux Microservices

### 1.1 Qu'est-ce qu'un microservice ?

Un **microservice** est un composant logiciel autonome qui :
- Exécute **une seule responsabilité métier** (Single Responsibility Principle)
- Possède **sa propre base de données** (pas de BDD partagée)
- Communique avec les autres services via des **protocoles réseau** (HTTP/REST, gRPC, messages)
- Peut être **déployé, mis à jour et scalé indépendamment**
- Est **conteneurisé** (Docker) et **orchestré** (Kubernetes)

### 1.2 Monolithe vs Microservices

```mermaid
flowchart LR
    subgraph Monolithe
        direction TB
        A["UI + Auth + Users + Lessons + Sessions"]
        DB1[(Unique BDD)]
        A --> DB1
    end

    subgraph Microservices
        direction TB
        GW["API Gateway"]
        S1["User Service"]
        S2["Learning Service"]
        S3["Session Service"]
        DB2[(PostgreSQL)]
        DB3[(MongoDB)]
        DB4[(Redis)]
        GW --> S1
        GW --> S2
        GW --> S3
        S1 --> DB2
        S2 --> DB3
        S3 --> DB4
    end
```

| Critère | Monolithe | Microservices |
|---------|-----------|---------------|
| **Déploiement** | Tout ou rien | Service par service |
| **Scaling** | Vertical (plus de RAM/CPU) | Horizontal (plus d'instances) |
| **Technologie** | Un seul langage/framework | Polyglotte possible |
| **Résilience** | Un bug = tout tombe | Un service tombe, les autres fonctionnent |
| **Complexité** | Simple au départ | Complexe au départ, scalable ensuite |
| **Base de données** | Unique, partagée | Une par service (isolation) |

### 1.3 Pourquoi des microservices pour Cube.com ?

Notre application se découpe naturellement en **domaines métier distincts** :

1. **Gestion des utilisateurs** → authentification, profils, statistiques
2. **Contenu pédagogique** → leçons, algorithmes (OLL/PLL/F2L), scrambles
3. **Sessions de jeu** → chronomètre, matchmaking, duels en temps réel

Chaque domaine a des **besoins techniques différents** :
- Les utilisateurs nécessitent des **transactions ACID** → PostgreSQL
- Le contenu est **semi-structuré et en lecture** → MongoDB
- Les sessions sont **éphémères et temps réel** → Redis + WebSocket

> [!NOTE]
> Le choix microservices est ici aussi motivé par les **contraintes du TP** : le barème valorise
> l'intégration de plusieurs services communicants via une gateway sur Kubernetes.

### 1.4 Les patterns fondamentaux

#### Pattern 1 : Database-per-Service
Chaque microservice possède et gère exclusivement sa propre base de données.
Aucun autre service n'accède directement à cette BDD.

```
❌ INTERDIT : Session Service → SELECT * FROM users (BDD du User Service)
✅ CORRECT  : Session Service → GET /api/users/{id} (API du User Service)
              ou via gRPC : UserService.GetUser(user_id)
```

#### Pattern 2 : API Gateway
Un point d'entrée unique pour tous les clients. Le client ne connaît qu'une seule URL.

```
Client → https://cube.com/api/users/me     → routé vers User Service
Client → https://cube.com/api/lessons       → routé vers Learning Service
Client → https://cube.com/api/sessions/solo → routé vers Session Service
```

#### Pattern 3 : Service Discovery
Dans Kubernetes, chaque service est accessible par son **nom DNS interne** :
```
user-service.cube.svc.cluster.local:8001
learning-service.cube.svc.cluster.local:8002
session-service.cube.svc.cluster.local:8003
```
Pas besoin de hardcoder des adresses IP !

---

## 2. Architecture globale de Cube.com

### 2.1 Vue d'ensemble

```mermaid
flowchart TD
    USER["🧑‍💻 Utilisateur\n(Navigateur)"]
    
    subgraph CLUSTER["☸ Cluster Kubernetes"]
        INGRESS["🔀 Nginx Ingress Controller\n(API Gateway)"]
        
        subgraph FRONTEND["Frontend Pod"]
            REACT["⚛️ React App\n(Nginx)"]
        end
        
        subgraph BACKEND["Backend Pods"]
            US["👤 User Service\nFastAPI :8001"]
            LS["📚 Learning Service\nFastAPI :8002"]
            SS["🎮 Session Service\nFastAPI :8003"]
        end
        
        subgraph DATA["Data Layer Pods"]
            PG[(PostgreSQL\n:5432)]
            MONGO[(MongoDB\n:27017)]
            REDIS[(Redis\n:6379)]
        end
        
        INGRESS -->|"/"| REACT
        INGRESS -->|"/api/users/*"| US
        INGRESS -->|"/api/lessons/*"| LS
        INGRESS -->|"/api/sessions/*"| SS
        US --> PG
        LS --> MONGO
        SS --> REDIS
        SS -.->|"gRPC :50051"| US
    end
    
    USER -->|"HTTPS"| INGRESS
```

### 2.2 Flux de données — Exemple : Un utilisateur lance un solve

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant F as React Frontend
    participant GW as Nginx Gateway
    participant SS as Session Service
    participant LS as Learning Service
    participant US as User Service
    participant R as Redis
    participant PG as PostgreSQL

    U->>F: Clique "Start Timer"
    F->>GW: GET /api/lessons/scrambles/random
    GW->>LS: Proxy → GET /scrambles/random
    LS-->>GW: { scramble: "R U R' U' R' F R2..." }
    GW-->>F: Scramble affiché

    U->>F: Mélange le cube, lance le chrono
    Note over U,F: L'utilisateur résout le cube...
    U->>F: Appuie sur Espace (stop timer)

    F->>GW: POST /api/sessions/solo/end { time_ms: 12450, scramble: "..." }
    GW->>SS: Proxy → POST /solo/end
    SS->>R: ZADD solves:user123 12450 "solve_id"
    SS->>US: gRPC → UpdateStats(user_id, 12450, scramble)
    US->>PG: INSERT INTO solve_times (...) VALUES (...)
    US->>PG: UPDATE users SET personal_best = ... WHERE ...
    US-->>SS: StatsResponse { pb: 11200, ao5: 13.4, ... }
    SS-->>GW: { time_ms: 12450, is_pb: false, stats: {...} }
    GW-->>F: Résultat affiché
    F->>U: "12.45s — AO5: 13.40s"
```

### 2.3 Les trois microservices en détail

#### 👤 User & Progression Service

| Aspect | Détail |
|--------|--------|
| **Responsabilité** | Auth, profils, statistiques, achievements |
| **Framework** | FastAPI (Python 3.12) |
| **Base de données** | PostgreSQL 16 (via SQLAlchemy async) |
| **Port** | 8001 |
| **Endpoints clés** | `POST /auth/register`, `POST /auth/login`, `GET /me`, `GET /me/stats` |
| **gRPC** | Expose `GetUser`, `ValidateToken`, `UpdateStats` pour les autres services |

#### 📚 Learning & Content Service

| Aspect | Détail |
|--------|--------|
| **Responsabilité** | Leçons Fridrich, algorithmes OLL/PLL/F2L, génération de scrambles |
| **Framework** | FastAPI (Python 3.12) |
| **Base de données** | MongoDB 7 (via Motor/Beanie ODM) |
| **Port** | 8002 |
| **Endpoints clés** | `GET /lessons`, `GET /algorithms?category=pll`, `GET /scrambles/random` |

#### 🎮 Session & Matchmaking Service

| Aspect | Détail |
|--------|--------|
| **Responsabilité** | Chronomètre, sessions solo, matchmaking ranked, duels temps réel |
| **Framework** | FastAPI (Python 3.12) |
| **Base de données** | Redis 7 (sessions éphémères, queues matchmaking) |
| **Port** | 8003 |
| **Endpoints clés** | `POST /solo/start`, `POST /solo/end`, `POST /matchmaking/join` |
| **Temps réel** | WebSocket à `/ws` pour les duels |
| **gRPC** | Appelle `UserService.UpdateStats` et `UserService.ValidateToken` |

---

## 3. Docker — Conteneurisation

### 3.1 Qu'est-ce que Docker ?

Docker permet d'**empaqueter une application et toutes ses dépendances** dans une image portable
appelée **conteneur**. Un conteneur est comme une "mini-machine virtuelle" légère qui contient :
- Le système de fichiers (OS minimal, code, bibliothèques)
- Les variables d'environnement
- Les ports exposés
- La commande de démarrage

```mermaid
flowchart LR
    subgraph IMAGE["📦 Image Docker"]
        OS["Alpine Linux 3.19"]
        PY["Python 3.12"]
        DEPS["FastAPI, SQLAlchemy..."]
        CODE["app/"]
    end
    
    IMAGE -->|"docker run"| C1["🟢 Conteneur 1\n(instance)"]
    IMAGE -->|"docker run"| C2["🟢 Conteneur 2\n(instance)"]
    IMAGE -->|"docker run"| C3["🟢 Conteneur 3\n(instance)"]
```

### 3.2 Dockerfile — Construction d'une image

Voici le Dockerfile du **User Service**, commenté ligne par ligne :

```dockerfile
# ============================================================
# STAGE 1 : Construction (Builder)
# ============================================================
# On part d'une image Python légère (slim = sans les extras)
FROM python:3.12-slim AS builder

# Répertoire de travail dans le conteneur
WORKDIR /app

# Empêcher Python de créer des fichiers .pyc et
# d'utiliser un buffer sur stdout (logs en temps réel)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copier UNIQUEMENT requirements.txt d'abord
# → Docker met en cache cette couche (layer caching)
# → Si requirements.txt n'a pas changé, pas de reinstall !
COPY requirements.txt .

# Installer les dépendances dans un dossier isolé
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# STAGE 2 : Production (Runtime)
# ============================================================
FROM python:3.12-slim

WORKDIR /app

# Copier les dépendances installées depuis le builder
# → L'image finale ne contient PAS pip, gcc, etc.
COPY --from=builder /install /usr/local

# Copier le code source de l'application
COPY ./app ./app

# Exposer le port du service (documentation)
EXPOSE 8001

# Utilisateur non-root pour la sécurité
RUN adduser --disabled-password --no-create-home appuser
USER appuser

# Commande de démarrage
# --host 0.0.0.0 : écouter sur toutes les interfaces réseau
# --port 8001    : port du service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

> [!IMPORTANT]
> **Le multi-stage build** est essentiel : l'image finale ne contient que Python + les libs +
> le code. Pas de compilateur, pas de pip → image ~150 Mo au lieu de ~800 Mo.

### 3.3 Layer Caching — Pourquoi l'ordre des instructions compte

Docker construit les images **couche par couche**. Chaque instruction `COPY`, `RUN`, etc.
crée une nouvelle couche. Si une couche n'a pas changé, Docker réutilise le cache.

```
COPY requirements.txt .      ← Change rarement  → cache réutilisé ✅
RUN pip install ...           ← Dépend du fichier au-dessus → cache ✅
COPY ./app ./app              ← Change souvent (votre code) → rebuild ici
```

**Règle d'or** : placer les instructions qui changent le moins souvent EN PREMIER.

### 3.4 Docker Compose — Orchestration locale

Docker Compose permet de définir et lancer **tous les services d'un coup** en local :

```yaml
# docker-compose.yml — Extrait commenté
services:
  # ─── Microservice 1 : User Service ───
  user-service:
    build:
      context: ./services/user-service     # Dossier contenant le Dockerfile
      dockerfile: Dockerfile
    ports:
      - "8001:8001"                        # host:conteneur
    environment:
      - POSTGRES_HOST=postgres             # Nom DNS du conteneur postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=cube_users
    depends_on:
      postgres:
        condition: service_healthy          # Attend que PG soit prêt
    networks:
      - cube-network                       # Réseau interne partagé

  # ─── Base de données PostgreSQL ───
  postgres:
    image: postgres:16-alpine              # Image officielle
    volumes:
      - postgres-data:/var/lib/postgresql/data  # Persistance !
    environment:
      POSTGRES_DB: cube_users
      POSTGRES_USER: cube
      POSTGRES_PASSWORD: changeme
    healthcheck:                           # K8s-style health check
      test: ["CMD-SHELL", "pg_isready -U cube"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - cube-network

networks:
  cube-network:                            # Réseau bridge isolé
    driver: bridge

volumes:
  postgres-data:                           # Volume nommé = persistant
```

> [!TIP]
> **`depends_on` avec `condition: service_healthy`** garantit que PostgreSQL accepte les
> connexions AVANT que le User Service ne démarre. Sans ça, FastAPI crasherait en essayant
> de se connecter à une BDD pas encore prête.

### 3.5 Commandes Docker essentielles

```bash
# Construire toutes les images
docker compose build

# Démarrer tous les services en arrière-plan
docker compose up -d

# Voir les logs en temps réel
docker compose logs -f user-service

# Reconstruire et relancer un service spécifique
docker compose up -d --build user-service

# Arrêter et supprimer tout (mais garder les volumes)
docker compose down

# Tout supprimer y compris les volumes (⚠️ perte de données)
docker compose down -v

# Publier une image sur Docker Hub
docker tag cube-user-service:latest monuser/cube-user-service:v1.0
docker push monuser/cube-user-service:v1.0
```

---

## 4. Kubernetes — Orchestration

### 4.1 Qu'est-ce que Kubernetes ?

**Kubernetes** (K8s) est un orchestrateur de conteneurs. Il automatise :
- Le **déploiement** des conteneurs sur un cluster de machines
- Le **scaling** (augmenter/réduire le nombre d'instances)
- La **résilience** (redémarrer un conteneur qui crash)
- Le **networking** (routage, load balancing, DNS interne)
- La **gestion des secrets** et de la configuration

### 4.2 Les objets Kubernetes fondamentaux

```mermaid
flowchart TD
    subgraph CLUSTER["☸ Cluster Kubernetes"]
        subgraph NS["Namespace: cube"]
            ING["Ingress\n(API Gateway)"]
            
            subgraph DEP1["Deployment: user-service"]
                RS1["ReplicaSet"]
                P1A["Pod 1a"]
                P1B["Pod 1b"]
                RS1 --> P1A
                RS1 --> P1B
            end
            
            SVC1["Service: user-service\n(ClusterIP)"]
            
            CM["ConfigMap\n(config)"]
            SEC["Secret\n(passwords)"]
            
            ING --> SVC1
            SVC1 --> P1A
            SVC1 --> P1B
            CM -.-> P1A
            SEC -.-> P1A
        end
    end
```

| Objet | Rôle | Analogie |
|-------|------|----------|
| **Pod** | Plus petite unité déployable. Contient 1+ conteneur(s). | Un conteneur qui tourne |
| **Deployment** | Gère les Pods : nombre de réplicas, mises à jour, rollbacks. | Le "chef d'orchestre" des Pods |
| **Service** | Donne un nom DNS stable et un load balancer interne aux Pods. | L'annuaire téléphonique |
| **Ingress** | Point d'entrée HTTP(S) depuis l'extérieur du cluster. | Le portier/routeur |
| **ConfigMap** | Configuration non-sensible (URLs, ports...). | Fichier .env |
| **Secret** | Données sensibles chiffrées (mots de passe, clés JWT). | Coffre-fort |
| **Namespace** | Isolation logique des ressources. | Un dossier de rangement |
| **PersistentVolumeClaim** | Demande de stockage persistant pour les BDD. | Un disque dur |

### 4.3 Deployment — Déployer un microservice

```yaml
# k8s/base/user-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: cube
  labels:
    app: user-service               # Label pour identifier ce Deployment
    tier: backend                   # Catégorisation (backend/frontend/data)
spec:
  replicas: 2                      # ← NOMBRE D'INSTANCES (Pods)
                                   # K8s maintient TOUJOURS 2 Pods actifs
                                   # Si un Pod crash, K8s en recrée un nouveau
  selector:
    matchLabels:
      app: user-service             # Le Deployment gère les Pods avec CE label
  template:                         # ← Template de Pod
    metadata:
      labels:
        app: user-service
    spec:
      containers:
        - name: user-service
          image: cube-user-service:latest   # Image Docker à utiliser
          ports:
            - containerPort: 8001

          # === PROBES DE SANTÉ ===
          # Kubernetes utilise ces endpoints pour savoir si le Pod est vivant

          # Liveness: "Le conteneur est-il vivant ?"
          # Si échec → K8s REDÉMARRE le conteneur
          livenessProbe:
            httpGet:
              path: /health
              port: 8001
            initialDelaySeconds: 10   # Attendre 10s avant le 1er check
            periodSeconds: 30         # Vérifier toutes les 30s

          # Readiness: "Le conteneur est-il PRÊT à recevoir du trafic ?"
          # Si échec → K8s RETIRE le Pod du load balancer (plus de trafic)
          readinessProbe:
            httpGet:
              path: /health
              port: 8001
            initialDelaySeconds: 5
            periodSeconds: 10

          # === LIMITES DE RESSOURCES ===
          resources:
            requests:               # Minimum garanti
              memory: "128Mi"
              cpu: "100m"           # 100 millicores = 0.1 CPU
            limits:                 # Maximum autorisé
              memory: "256Mi"
              cpu: "250m"

          # === VARIABLES D'ENVIRONNEMENT ===
          env:
            - name: POSTGRES_HOST
              value: "postgres"     # Nom DNS du Service PostgreSQL
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:       # ← Lue depuis un Secret K8s
                  name: postgres-secret
                  key: password
```

> [!IMPORTANT]
> **Liveness vs Readiness Probes** — C'est une distinction critique :
> - **Liveness** : "Es-tu vivant ?" → Non → Redémarrage du conteneur
> - **Readiness** : "Es-tu prêt ?" → Non → Retiré du load balancer (pas de kill)
>
> Exemple : au démarrage, un service peut être vivant mais pas prêt (attend la connexion BDD).

### 4.4 Service — Exposer un Pod en réseau

```yaml
# k8s/base/user-service/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service            # ← Ce nom devient le DNS interne !
  namespace: cube
spec:
  type: ClusterIP               # Accessible UNIQUEMENT à l'intérieur du cluster
  selector:
    app: user-service            # Cible les Pods avec ce label
  ports:
    - port: 8001                 # Port du Service
      targetPort: 8001           # Port du conteneur dans le Pod
      protocol: TCP
```

**Comment ça marche :**
```
Autre Pod → http://user-service:8001/health
                    ↑
                    DNS interne Kubernetes
                    résolu automatiquement vers l'IP d'un des Pods
                    avec load balancing round-robin
```

Le Service agit comme un **load balancer interne** : si vous avez 2 réplicas du User Service,
les requêtes sont distribuées alternativement entre les deux Pods.

### 4.5 Commandes kubectl essentielles

```bash
# Voir tous les Pods dans le namespace 'cube'
kubectl get pods -n cube

# Voir les logs d'un Pod
kubectl logs -f user-service-7d8b9c6f4-x2k9j -n cube

# Appliquer un fichier de configuration
kubectl apply -f k8s/base/user-service/deployment.yaml

# Appliquer tout un dossier
kubectl apply -f k8s/base/ -R    # -R = récursif

# Scaling manuel (passer à 3 réplicas)
kubectl scale deployment user-service --replicas=3 -n cube

# Entrer dans un Pod pour débugger
kubectl exec -it user-service-7d8b9c6f4-x2k9j -n cube -- /bin/sh

# Port-forward pour accéder en local (sans Ingress)
kubectl port-forward svc/user-service 8001:8001 -n cube

# Voir les événements (utile pour le debug)
kubectl get events -n cube --sort-by='.lastTimestamp'
```

---

## 5. FastAPI — Le framework backend

### 5.1 Pourquoi FastAPI ?

FastAPI est un framework web Python **moderne, rapide et auto-documenté** :

| Feature | Détail |
|---------|--------|
| **Performance** | Basé sur Starlette (ASGI) et uvicorn → aussi rapide que Node.js/Go |
| **Type hints** | Validation automatique grâce à Pydantic |
| **Async natif** | Support `async/await` → parfait pour I/O (BDD, HTTP, gRPC) |
| **OpenAPI auto** | Documentation Swagger générée automatiquement |
| **Dependency Injection** | Système `Depends()` pour l'injection de dépendances |

### 5.2 Structure d'un microservice FastAPI

Chaque service suit une **architecture en couches** (layered architecture) :

```
app/
├── main.py          ← Point d'entrée, configuration FastAPI
├── config.py        ← Variables d'environnement (Pydantic Settings)
├── api/             ← Couche HTTP (routes, validation)
│   └── v1/          ← Versionning d'API
│       ├── users.py
│       └── auth.py
├── schemas/         ← DTOs (Data Transfer Objects) — Pydantic
├── models/          ← ORM (mapping BDD) — SQLAlchemy
├── services/        ← Logique métier (pas de HTTP ici !)
└── db/              ← Connexion BDD, sessions
```

```mermaid
flowchart LR
    REQ["Requête HTTP"]
    API["api/v1/users.py\n(Router)"]
    SCH["schemas/user.py\n(Validation)"]
    SVC["services/user_service.py\n(Logique métier)"]
    MDL["models/user.py\n(ORM)"]
    DB[(PostgreSQL)]
    
    REQ -->|"JSON"| API
    API -->|"Pydantic"| SCH
    API -->|"Depends()"| SVC
    SVC --> MDL
    MDL -->|"SQL"| DB
```

> [!IMPORTANT]
> **Règle d'or de la séparation des couches :**
> - Les **routes** (`api/`) ne contiennent PAS de logique métier
> - Les **services** (`services/`) ne connaissent PAS HTTP (pas de Request, Response)
> - Les **modèles** (`models/`) ne connaissent PAS Pydantic
>
> Chaque couche ne dépend que de la couche en dessous, jamais au-dessus.

### 5.3 Point d'entrée — `main.py`

```python
"""User & Progression Service — Point d'entrée FastAPI.

Ce module configure l'application FastAPI :
- Lifespan events (startup/shutdown)
- Middlewares (CORS)
- Routes
- Health check
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.db.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire du cycle de vie de l'application.

    Le pattern 'lifespan' remplace les anciens @app.on_event("startup")
    et @app.on_event("shutdown"). Il utilise un context manager async :

    - AVANT 'yield' → code de démarrage (créer tables, connexions)
    - APRÈS 'yield' → code d'arrêt (fermer connexions, cleanup)

    Ce pattern garantit que les ressources sont toujours libérées,
    même en cas d'erreur.
    """
    # === STARTUP ===
    # Créer les tables en BDD (en dev uniquement)
    # En production, utiliser Alembic pour les migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")

    yield  # ← L'application tourne ici

    # === SHUTDOWN ===
    await engine.dispose()
    print("🔌 Database connections closed")


app = FastAPI(
    title="Cube - User Service",
    description="Gestion des utilisateurs et de la progression",
    version="1.0.0",
    lifespan=lifespan,
    # root_path est utilisé quand le service est derrière un reverse proxy
    # L'Ingress route /api/users/* vers ce service
    root_path="/api/users",
)

# === CORS Middleware ===
# Nécessaire pour que le frontend React (port 3000) puisse appeler
# le backend (port 8001) sans erreur CORS du navigateur
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:3000"]
    allow_credentials=True,               # Permettre les cookies/JWT
    allow_methods=["*"],                  # GET, POST, PUT, DELETE...
    allow_headers=["*"],                  # Authorization, Content-Type...
)

# Inclure toutes les routes
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Endpoint de santé pour les probes Kubernetes.

    Kubernetes appelle cet endpoint régulièrement pour vérifier
    que le service est vivant (liveness) et prêt (readiness).

    Retourne un simple JSON : { "status": "healthy" }
    """
    return {"status": "healthy", "service": "user-service"}
```

### 5.4 Configuration — `config.py` (Pydantic Settings)

```python
"""Configuration centralisée via variables d'environnement.

Pydantic Settings lit automatiquement les variables d'environnement
et les valide au démarrage. Si une variable obligatoire manque,
l'application refuse de démarrer → fail fast.

Exemple :
    POSTGRES_HOST=localhost → settings.POSTGRES_HOST == "localhost"
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration du User Service.

    Chaque attribut correspond à une variable d'environnement.
    Les valeurs par défaut servent pour le développement local.
    """

    # === Base de données ===
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "cube_users"
    POSTGRES_USER: str = "cube"
    POSTGRES_PASSWORD: str = "changeme"

    @property
    def DATABASE_URL(self) -> str:
        """Construit l'URL de connexion PostgreSQL.

        Format : postgresql+asyncpg://user:password@host:port/database
                  └── driver ──┘       └── auth ──┘ └─ host ─┘ └─ db ─┘

        'asyncpg' est le driver asynchrone pour PostgreSQL.
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # === JWT (JSON Web Tokens) ===
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30

    # === CORS ===
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]

    # === gRPC ===
    GRPC_PORT: int = 50051

    class Config:
        env_file = ".env"        # Charger les vars depuis un fichier .env
        case_sensitive = True    # POSTGRES_HOST ≠ postgres_host


# Singleton : une seule instance partagée dans toute l'app
settings = Settings()
```

### 5.5 Modèles ORM — `models/user.py` (SQLAlchemy)

```python
"""Modèles SQLAlchemy pour la table 'users'.

SQLAlchemy est un ORM (Object-Relational Mapping) :
il fait le pont entre les objets Python et les tables SQL.

    Classe Python User ←→ Table SQL 'users'
    user.username      ←→ colonne 'username'
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


class User(Base):
    """Modèle utilisateur.

    Chaque instance de cette classe correspond à une ligne
    dans la table 'users' de PostgreSQL.
    """
    __tablename__ = "users"

    # UUID v4 comme clé primaire (pas d'auto-increment)
    # → Plus sûr (pas de devinette d'ID séquentiel)
    # → Compatible distribué (pas de conflit entre services)
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)

    # server_default=func.now() → la valeur est générée par PostgreSQL
    # (plus fiable que datetime.utcnow() côté Python)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # Mis à jour automatiquement
    )
```

### 5.6 Schemas Pydantic — `schemas/user.py`

```python
"""Schemas Pydantic pour la validation des données.

Les schemas définissent la FORME des données qui entrent et sortent de l'API :
- UserCreate : ce que le client ENVOIE pour créer un utilisateur
- UserResponse : ce que l'API RETOURNE

Pydantic valide automatiquement les données :
- Type incorrect → erreur 422
- Champ manquant → erreur 422
- Email invalide → erreur 422
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# === ENTRÉE (ce que le client envoie) ===

class UserCreate(BaseModel):
    """Schema pour la création d'un utilisateur.

    Exemple de requête :
        POST /auth/register
        {
            "username": "speedcuber42",
            "email": "cube@example.com",
            "password": "MyStr0ngP@ss!"
        }
    """
    username: str = Field(
        ...,                    # ... = obligatoire
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",  # Alphanumeric + tirets
        examples=["speedcuber42"],
    )
    email: EmailStr             # Validation email automatique
    password: str = Field(
        ...,
        min_length=8,
        examples=["MyStr0ngP@ss!"],
    )


class UserLogin(BaseModel):
    """Schema pour la connexion."""
    email: EmailStr
    password: str


# === SORTIE (ce que l'API retourne) ===

class UserResponse(BaseModel):
    """Schema de réponse utilisateur.

    Note : le mot de passe n'est JAMAIS retourné !

    model_config avec from_attributes=True permet à Pydantic
    de lire les attributs d'un objet SQLAlchemy directement.
    """
    id: UUID
    username: str
    email: EmailStr
    avatar_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# === JWT Tokens ===

class Token(BaseModel):
    """Réponse après connexion réussie."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Contenu décodé d'un JWT."""
    sub: str        # Subject = user_id
    exp: datetime   # Expiration
```

### 5.7 Dependency Injection — Le système `Depends()`

```python
"""Injection de dépendances avec FastAPI.

Depends() permet d'injecter automatiquement des dépendances
dans les fonctions de route. C'est le CŒUR de FastAPI.

Chaîne de dépendances :
    Route → get_current_user → verify_token → get_db
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.auth_service import verify_token

# OAuth2PasswordBearer extrait le token du header Authorization
# Header attendu : "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),    # ← Injecté automatiquement
    db: AsyncSession = Depends(get_db),     # ← Injecté automatiquement
):
    """Dépendance qui récupère l'utilisateur connecté.

    FastAPI exécute cette chaîne automatiquement :
    1. Extraire le token JWT du header Authorization
    2. Décoder et vérifier le token
    3. Récupérer l'utilisateur en BDD
    4. Retourner l'objet User

    Si le token est invalide → HTTPException 401
    Si l'utilisateur n'existe pas → HTTPException 404
    """
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, payload.sub)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user


# === Utilisation dans une route ===

@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    # ↑ FastAPI injecte automatiquement l'utilisateur connecté
    # Si pas connecté → 401 avant même d'entrer dans la fonction
):
    """Récupère le profil de l'utilisateur connecté."""
    return current_user
```

### 5.8 Connexion asynchrone à PostgreSQL

```python
"""Configuration de la connexion asynchrone à PostgreSQL.

SQLAlchemy 2.0 supporte l'async via asyncpg.
L'async est crucial en microservices car un service attend souvent
des réponses (BDD, autres services, Redis) et ne doit PAS bloquer.

Sync (bloquant) :
    Thread 1: [──requête BDD──────────] → bloqué pendant 50ms
    Thread 2: [attente...              ] → ne peut rien faire

Async (non-bloquant) :
    Task 1: [──req BDD──→ yield ──reprise──]
    Task 2: [            ──exécute──       ] → utilise le temps libre
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# === Engine : le "moteur" de connexion à la BDD ===
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,        # True pour voir les requêtes SQL en dev
    pool_size=20,      # Nombre de connexions dans le pool
    max_overflow=10,   # Connexions supplémentaires en cas de pic
)

# === Session Factory ===
# async_sessionmaker crée des sessions de BDD réutilisables
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Les objets restent accessibles après commit
)

# === Base class pour tous les modèles ===
class Base(DeclarativeBase):
    pass


# === Dépendance FastAPI ===
async def get_db():
    """Fournit une session de BDD par requête HTTP.

    Utilise le pattern 'session-per-request' :
    - Chaque requête HTTP reçoit sa propre session
    - La session est automatiquement fermée à la fin

    'yield' permet à FastAPI de gérer le cycle de vie :
    - Avant yield → session ouverte
    - Après yield → session fermée (même en cas d'erreur)
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

## 6. Communication inter-services : REST vs gRPC

### 6.1 Deux styles de communication

```mermaid
flowchart LR
    subgraph REST["REST (HTTP/JSON)"]
        direction LR
        C1["Client / Frontend"]
        S1["Service"]
        C1 -->|"GET /users/123\nContent-Type: application/json"| S1
        S1 -->|"200 OK\n{\"username\": \"...\"}"| C1
    end
    
    subgraph GRPC["gRPC (HTTP/2 + Protobuf)"]
        direction LR
        C2["Session Service"]
        S2["User Service"]
        C2 -->|"UserService.GetUser()\nBinaire Protobuf"| S2
        S2 -->|"UserResponse\nBinaire Protobuf"| C2
    end
```

| Critère | REST | gRPC |
|---------|------|------|
| **Format** | JSON (texte, lisible) | Protobuf (binaire, compact) |
| **Protocole** | HTTP/1.1 | HTTP/2 (multiplexing) |
| **Performance** | ~1x | ~7-10x plus rapide |
| **Contrat** | OpenAPI/Swagger (optionnel) | `.proto` (obligatoire, strict) |
| **Streaming** | Non natif | Bidirectionnel natif |
| **Usage** | Client ↔ Backend | Service ↔ Service |
| **Debug** | Facile (curl, Postman) | Plus complexe |

### 6.2 Quand utiliser quoi dans Cube.com ?

```
Frontend React ──REST──→ API Gateway ──REST──→ Services
                                                 ↕
                                      Service ──gRPC──→ Service
```

- **REST** : Communication client → serveur (le navigateur ne parle pas gRPC)
- **gRPC** : Communication inter-services (plus rapide, contrat strict)

### 6.3 Protocol Buffers — Le contrat d'interface gRPC

```protobuf
// proto/user.proto
//
// Ce fichier définit le CONTRAT entre les services.
// C'est un "schéma" strict qui garantit que les deux services
// parlent le même langage.
//
// À partir de ce fichier, grpcio-tools génère :
// - user_pb2.py       → classes Python pour les messages
// - user_pb2_grpc.py  → client et serveur gRPC

syntax = "proto3";        // Version du langage Protobuf

package cube.user;        // Namespace pour éviter les conflits

// === SERVICE : définit les méthodes appelables à distance ===
service UserService {
    // Chaque 'rpc' est une méthode que le Session Service peut appeler
    rpc GetUser (GetUserRequest) returns (UserResponse);
    rpc ValidateToken (ValidateTokenRequest) returns (ValidateTokenResponse);
    rpc UpdateStats (UpdateStatsRequest) returns (StatsResponse);
}

// === MESSAGES : les structures de données échangées ===
// Chaque champ a un numéro unique (1, 2, 3...)
// Ce numéro est utilisé dans l'encodage binaire (pas le nom !)
// → On peut renommer un champ sans casser la compatibilité

message GetUserRequest {
    string user_id = 1;       // Champ 1 : identifiant UUID
}

message UserResponse {
    string user_id = 1;
    string username = 2;
    string avatar_url = 3;
    int32 rating = 4;         // Rating Elo pour le matchmaking
}
```

### 6.4 Compilation et utilisation de gRPC en Python

```bash
# Compiler les fichiers .proto en Python
python -m grpc_tools.protoc \
    -I./proto \                          # Dossier des .proto
    --python_out=./services/user-service/app/grpc_gen \   # Classes de messages
    --grpc_python_out=./services/user-service/app/grpc_gen \  # Client/Serveur
    proto/user.proto
```

**Côté serveur (User Service)** — Implémente les méthodes gRPC :

```python
"""Serveur gRPC du User Service.

Ce serveur écoute sur le port 50051 et traite les appels gRPC
venant des autres services (Session Service, etc.)
"""
import grpc
from concurrent import futures

from app.grpc_gen import user_pb2, user_pb2_grpc
from app.services.user_service import get_user_by_id, update_user_stats


class UserServicer(user_pb2_grpc.UserServiceServicer):
    """Implémentation du service gRPC UserService.

    Chaque méthode correspond à un 'rpc' défini dans user.proto.
    """

    async def GetUser(self, request, context):
        """Récupère un utilisateur par son ID.

        Args:
            request: GetUserRequest contenant user_id
            context: Métadonnées gRPC (deadlines, auth, etc.)

        Returns:
            UserResponse avec les infos de l'utilisateur
        """
        user = await get_user_by_id(request.user_id)
        if user is None:
            # Équivalent d'un 404 en REST
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User {request.user_id} not found")
            return user_pb2.UserResponse()

        return user_pb2.UserResponse(
            user_id=str(user.id),
            username=user.username,
            avatar_url=user.avatar_url or "",
            rating=user.rating,
        )
```

**Côté client (Session Service)** — Appelle le User Service :

```python
"""Client gRPC pour appeler le User Service.

Depuis le Session Service, on utilise ce client pour :
- Vérifier un token JWT (avant d'accepter une connexion WebSocket)
- Mettre à jour les stats après un solve
"""
import grpc
from app.grpc_gen import user_pb2, user_pb2_grpc
from app.config import settings


class UserGRPCClient:
    """Client gRPC vers le User Service."""

    def __init__(self):
        # Canal gRPC (connexion au serveur)
        # En K8s : "user-service:50051" (DNS interne)
        self.channel = grpc.aio.insecure_channel(
            f"{settings.USER_SERVICE_GRPC_HOST}:{settings.USER_SERVICE_GRPC_PORT}"
        )
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)

    async def get_user(self, user_id: str):
        """Appel gRPC : récupère les infos d'un utilisateur."""
        request = user_pb2.GetUserRequest(user_id=user_id)
        try:
            response = await self.stub.GetUser(request)
            return {
                "user_id": response.user_id,
                "username": response.username,
                "rating": response.rating,
            }
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise

    async def update_stats(self, user_id: str, solve_time_ms: int, scramble: str):
        """Appel gRPC : met à jour les stats après un solve."""
        request = user_pb2.UpdateStatsRequest(
            user_id=user_id,
            solve_time_ms=solve_time_ms,
            scramble=scramble,
        )
        return await self.stub.UpdateStats(request)

    async def close(self):
        """Ferme proprement la connexion gRPC."""
        await self.channel.close()


# Singleton
user_grpc_client = UserGRPCClient()
```

---

## 7. Bases de données — Le pattern Database-per-Service

### 7.1 Pourquoi une BDD par service ?

```mermaid
flowchart TD
    subgraph ANTI["❌ Anti-pattern : BDD partagée"]
        S1A["User Service"] --> DB1[(Unique BDD)]
        S2A["Learning Service"] --> DB1
        S3A["Session Service"] --> DB1
    end
    
    subgraph CORRECT["✅ Pattern : Database-per-Service"]
        S1B["User Service"] --> DB2[(PostgreSQL)]
        S2B["Learning Service"] --> DB3[(MongoDB)]
        S3B["Session Service"] --> DB4[(Redis)]
    end
```

| BDD partagée (anti-pattern) | BDD par service (correct) |
|----|-----|
| Un changement de schéma casse tous les services | Chaque service évolue indépendamment |
| Couplage fort entre services | Couplage faible |
| Impossible de choisir la meilleure BDD par cas | Chaque service utilise la BDD optimale |
| Single point of failure | Résilience : une BDD tombe, un seul service affecté |

### 7.2 PostgreSQL — User Service (données relationnelles)

**Pourquoi PostgreSQL pour les utilisateurs ?**
- Les utilisateurs ont des **relations** : un utilisateur a N solve_times, N achievements
- On a besoin de **transactions ACID** : inscription = créer user + hasher password (atomique)
- Les statistiques nécessitent des **requêtes SQL** complexes (AVG, MIN, COUNT...)

```python
"""Exemple : calcul des statistiques Average of 5 (AO5).

L'Average of 5 en speedcubing = moyenne des 5 derniers solves
en retirant le meilleur et le pire temps.

Requête SQL équivalente :
    WITH recent_5 AS (
        SELECT time_ms FROM solve_times
        WHERE user_id = :uid
        ORDER BY created_at DESC LIMIT 5
    )
    SELECT AVG(time_ms) FROM (
        SELECT time_ms FROM recent_5
        ORDER BY time_ms
        OFFSET 1 LIMIT 3       -- Enlève le min et le max
    )
"""
from sqlalchemy import select, func
from app.models.stats import SolveTime


async def calculate_ao5(db, user_id: str) -> float | None:
    """Calcule l'Average of 5 pour un utilisateur."""
    # Récupérer les 5 derniers temps
    stmt = (
        select(SolveTime.time_ms)
        .where(SolveTime.user_id == user_id)
        .order_by(SolveTime.created_at.desc())
        .limit(5)
    )
    result = await db.execute(stmt)
    times = [row[0] for row in result.fetchall()]

    if len(times) < 5:
        return None

    # Retirer le meilleur et le pire
    times.sort()
    trimmed = times[1:-1]  # Enlève index 0 (min) et -1 (max)

    return sum(trimmed) / len(trimmed)
```

### 7.3 MongoDB — Learning Service (documents semi-structurés)

**Pourquoi MongoDB pour le contenu ?**
- Les leçons sont des **documents** avec une structure variable (texte, étapes, vidéos...)
- Le schéma peut **évoluer** facilement (ajouter un champ sans migration)
- **Beanie** (ODM pour MongoDB) s'intègre parfaitement avec Pydantic/FastAPI

```python
"""Modèle MongoDB avec Beanie ODM.

Beanie = Pydantic + Motor (driver async MongoDB).
Un Document Beanie correspond à une collection MongoDB.
"""
from beanie import Document
from pydantic import Field


class Algorithm(Document):
    """Un algorithme de Rubik's Cube (OLL, PLL, F2L).

    Exemple de document MongoDB :
    {
        "_id": "...",
        "name": "T-Perm",
        "category": "PLL",
        "notation": "R U R' U' R' F R2 U' R' U' R U R' F'",
        "description": "Permutation en T — l'une des plus utilisées",
        "triggers": ["R U R'", "headlights on left"],
        "image_url": "/images/pll/t-perm.png"
    }
    """
    name: str
    category: str = Field(..., pattern=r"^(OLL|PLL|F2L|CROSS)$")
    notation: str                  # Notation standard Rubik's (R U R' ...)
    description: str = ""
    triggers: list[str] = []       # Cas de reconnaissance visuelle
    image_url: str | None = None

    class Settings:
        name = "algorithms"        # Nom de la collection MongoDB


class Lesson(Document):
    """Une leçon de la méthode Fridrich.

    La structure en 'steps' est typiquement semi-structurée :
    chaque leçon a un nombre variable d'étapes avec des contenus différents.
    C'est exactement le cas d'usage de MongoDB vs SQL.
    """
    title: str
    category: str                  # beginner, f2l, oll, pll
    difficulty: int = Field(..., ge=1, le=5)  # 1 à 5
    description: str
    steps: list[dict]              # Structure libre par étape
    video_url: str | None = None
    order: int                     # Ordre d'affichage

    class Settings:
        name = "lessons"
```

### 7.4 Redis — Session Service (données éphémères)

**Pourquoi Redis pour les sessions ?**
- Les sessions de solve sont **éphémères** (durée de vie = quelques minutes)
- Le matchmaking nécessite des **opérations temps réel** ultra-rapides (<1ms)
- Redis fonctionne **en mémoire** → latence ~0.1ms vs ~5ms pour PostgreSQL

```python
"""Utilisation de Redis pour le matchmaking.

Redis Sorted Sets = structure idéale pour le matchmaking :
- Chaque joueur a un SCORE (son rating Elo)
- ZRANGEBYSCORE trouve les joueurs dans une fourchette de rating
- Opérations en O(log N) → ultra-rapide même avec 100k joueurs

Commandes Redis utilisées :
- ZADD   : ajouter un joueur à la queue
- ZRANGEBYSCORE : trouver les joueurs proches en rating
- ZREM   : retirer un joueur de la queue
- SET/GET : stocker/lire une session (avec TTL)
"""
import json
import uuid
from datetime import timedelta

import redis.asyncio as redis
from app.config import settings


class MatchmakingService:
    """Service de matchmaking basé sur Redis Sorted Sets."""

    QUEUE_KEY = "matchmaking:queue"
    SESSION_PREFIX = "session:"
    MATCH_PREFIX = "match:"

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    async def join_queue(self, user_id: str, rating: int) -> dict | None:
        """Rejoint la file de matchmaking.

        1. Cherche un adversaire avec un rating proche (±100)
        2. Si trouvé → crée un match et retourne les détails
        3. Sinon → ajoute le joueur à la queue et attend

        Args:
            user_id: UUID de l'utilisateur
            rating: Rating Elo du joueur

        Returns:
            Match details si un adversaire est trouvé, None sinon
        """
        # Chercher un adversaire dans la fourchette [rating-100, rating+100]
        opponents = await self.redis.zrangebyscore(
            self.QUEUE_KEY,
            min=rating - 100,
            max=rating + 100,
            start=0,
            num=1,  # Un seul résultat suffit
        )

        if opponents:
            opponent_id = opponents[0].decode()
            if opponent_id != user_id:
                # Match trouvé ! Retirer l'adversaire de la queue
                await self.redis.zrem(self.QUEUE_KEY, opponent_id)

                # Créer le match
                match_id = str(uuid.uuid4())
                match_data = {
                    "match_id": match_id,
                    "player1": user_id,
                    "player2": opponent_id,
                    "scramble": generate_scramble(),
                    "status": "ready",
                }

                # Stocker le match dans Redis (expire après 30 min)
                await self.redis.set(
                    f"{self.MATCH_PREFIX}{match_id}",
                    json.dumps(match_data),
                    ex=timedelta(minutes=30),
                )
                return match_data

        # Pas d'adversaire trouvé → rejoindre la queue
        await self.redis.zadd(self.QUEUE_KEY, {user_id: rating})
        return None

    async def leave_queue(self, user_id: str):
        """Quitte la file de matchmaking."""
        await self.redis.zrem(self.QUEUE_KEY, user_id)
```

---

## 8. API Gateway — Nginx Ingress

### 8.1 Rôle de l'API Gateway

L'API Gateway est le **point d'entrée unique** de l'application.
Le client (React) ne connaît qu'une seule adresse : `https://cube.com`.
La gateway route les requêtes vers le bon microservice.

```mermaid
flowchart LR
    C["🌐 Client React"]
    
    subgraph GW["🔀 Nginx Ingress"]
        R1["/api/users/*"]
        R2["/api/lessons/*"]
        R3["/api/sessions/*"]
        R4["/*"]
    end
    
    US["👤 User Service"]
    LS["📚 Learning Service"]
    SS["🎮 Session Service"]
    FE["⚛️ Frontend"]
    
    C --> GW
    R1 --> US
    R2 --> LS
    R3 --> SS
    R4 --> FE
```

### 8.2 Pourquoi une Gateway ?

Sans gateway :
```
Client → http://user-service:8001/users     → CORS issues, pas de HTTPS
Client → http://learning-service:8002/lessons → URLs différentes
Client → http://session-service:8003/sessions → Complexe à gérer
```

Avec gateway :
```
Client → https://cube.com/api/users          → Simple, une seule URL
Client → https://cube.com/api/lessons        → HTTPS + CORS centralisé
Client → https://cube.com/api/sessions       → Transparent
```

### 8.3 Configuration Nginx Ingress

```yaml
# k8s/base/gateway/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cube-ingress
  namespace: cube
  annotations:
    # Classe du contrôleur Ingress à utiliser
    kubernetes.io/ingress.class: nginx

    # Réécrire l'URL avant de la transmettre au service
    # /api/users/me → /me (le service ne voit pas le préfixe)
    nginx.ingress.kubernetes.io/rewrite-target: /$2

    # Support WebSocket pour le Session Service
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"

    # CORS headers
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "*"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET,POST,PUT,DELETE,OPTIONS"
spec:
  rules:
    - host: cube.local              # Nom d'hôte (ajouter dans /etc/hosts)
      http:
        paths:
          # Route 1 : User Service
          - path: /api/users(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: user-service
                port:
                  number: 8001

          # Route 2 : Learning Service
          - path: /api/lessons(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: learning-service
                port:
                  number: 8002

          # Route 3 : Session Service
          - path: /api/sessions(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: session-service
                port:
                  number: 8003

          # Route 4 : Frontend (catch-all)
          - path: /(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: frontend
                port:
                  number: 80
```

### 8.4 Mise en place avec Minikube

```bash
# 1. Activer le addon Ingress dans Minikube
minikube addons enable ingress

# 2. Vérifier que le contrôleur tourne
kubectl get pods -n ingress-nginx

# 3. Récupérer l'IP de Minikube
minikube ip
# → 192.168.49.2

# 4. Ajouter dans /etc/hosts (Linux/Mac) ou C:\Windows\System32\drivers\etc\hosts
echo "192.168.49.2 cube.local" | sudo tee -a /etc/hosts

# 5. Tester
curl http://cube.local/api/users/health
# → {"status": "healthy", "service": "user-service"}
```

---

## 9. Sécurité du cluster

### 9.1 Vue d'ensemble des couches de sécurité

```mermaid
flowchart TD
    subgraph SEC["🔒 Couches de sécurité"]
        L1["1️⃣ Authentification JWT\n(Application level)"]
        L2["2️⃣ RBAC Kubernetes\n(Cluster level)"]
        L3["3️⃣ Network Policies\n(Network level)"]
        L4["4️⃣ mTLS / Service Mesh\n(Transport level)"]
        L5["5️⃣ Docker Image Security\n(Build level)"]
    end
    
    L1 --> L2 --> L3 --> L4 --> L5
```

### 9.2 JWT — Authentification applicative

```python
"""Authentification par JSON Web Token (JWT).

Un JWT est composé de 3 parties séparées par des points :
    header.payload.signature

Exemple décodé :
    Header:  { "alg": "HS256", "typ": "JWT" }
    Payload: { "sub": "user-uuid-123", "exp": 1699999999 }
    Signature: HMACSHA256(base64(header) + "." + base64(payload), SECRET_KEY)

Flux d'authentification :
    1. Client POST /auth/login { email, password }
    2. Serveur vérifie le mot de passe
    3. Serveur crée et retourne un JWT
    4. Client stocke le JWT (localStorage ou cookie)
    5. Client envoie le JWT dans chaque requête :
       Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
"""
from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

# Bcrypt pour le hashage de mots de passe
# Bcrypt est lent INTENTIONNELLEMENT (protection contre le brute-force)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt.

    'changeme' → '$2b$12$LJ3m4y3h5...' (hash irréversible)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    """Crée un JWT pour un utilisateur.

    Le token contient :
    - sub (subject) : l'identifiant de l'utilisateur
    - exp (expiration) : quand le token expire
    - iat (issued at) : quand le token a été créé

    Le token est SIGNÉ avec la clé secrète (pas chiffré !).
    N'importe qui peut LIRE le contenu, mais personne ne peut le MODIFIER.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """Vérifie et décode un JWT.

    Retourne le payload si le token est valide,
    None si le token est invalide ou expiré.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None
```

### 9.3 RBAC Kubernetes

```yaml
# k8s/security/rbac.yaml
#
# RBAC = Role-Based Access Control
# Principe du moindre privilège : chaque service n'a accès
# qu'aux ressources dont il a BESOIN.

# 1. Un ServiceAccount par microservice
apiVersion: v1
kind: ServiceAccount
metadata:
  name: user-service-sa
  namespace: cube
---
# 2. Un Role définit les PERMISSIONS
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: user-service-role
  namespace: cube
rules:
  # Ce service peut lire les ConfigMaps et Secrets
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list"]
    # PAS de "create", "update", "delete" → lecture seule
---
# 3. Un RoleBinding LIE le ServiceAccount au Role
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: user-service-binding
  namespace: cube
subjects:
  - kind: ServiceAccount
    name: user-service-sa
roleRef:
  kind: Role
  name: user-service-role
  apiGroup: rbac.authorization.k8s.io
```

### 9.4 Network Policies — Isolation réseau

```yaml
# k8s/security/network-policies.yaml
#
# Les Network Policies sont le "firewall" de Kubernetes.
# Par défaut, tous les Pods peuvent communiquer entre eux.
# Ces règles restreignent les flux autorisés.

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: postgres-network-policy
  namespace: cube
spec:
  # S'applique aux Pods avec le label app=postgres
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
    - Ingress     # Contrôle le trafic ENTRANT
  ingress:
    - from:
        # SEUL le User Service peut accéder à PostgreSQL
        - podSelector:
            matchLabels:
              app: user-service
      ports:
        - port: 5432
          protocol: TCP
# Résultat :
# ✅ user-service → postgres:5432    AUTORISÉ
# ❌ learning-service → postgres:5432 BLOQUÉ
# ❌ session-service → postgres:5432  BLOQUÉ
```

---

## 10. React & Frontend

### 10.1 Architecture du frontend

```
frontend/src/
├── main.tsx              ← Point d'entrée React
├── App.tsx               ← Routes et layout
├── components/
│   ├── cube/             ← Composant Cube 3D (Three.js / R3F)
│   ├── timer/            ← Chronomètre
│   └── common/           ← Composants réutilisables
├── pages/                ← Pages (une par route)
├── services/             ← Appels API (Axios)
├── hooks/                ← Custom hooks React
├── store/                ← State management (Zustand)
└── types/                ← Interfaces TypeScript
```

### 10.2 Client API — Communication avec les microservices

```typescript
// src/services/api.ts
//
// Instance Axios centralisée.
// Tous les appels API passent par cette instance.
// Le JWT est injecté automatiquement via un interceptor.

import axios from "axios";

const api = axios.create({
  // En dev : http://localhost:8080/api (gateway locale)
  // En prod : /api (même domaine, via Ingress)
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// === INTERCEPTOR DE REQUÊTE ===
// Ajoute automatiquement le JWT à chaque requête
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// === INTERCEPTOR DE RÉPONSE ===
// Gère les erreurs 401 (token expiré) globalement
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expiré → rediriger vers login
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
```

```typescript
// src/services/userService.ts
//
// Appels API vers le User Service.
// Chaque fonction correspond à un endpoint REST.

import api from "./api";
import type { User, UserCreate, Token, Stats } from "../types";

export const userService = {
  /** POST /users/auth/register */
  register: (data: UserCreate) =>
    api.post<Token>("/users/auth/register", data),

  /** POST /users/auth/login */
  login: (email: string, password: string) =>
    api.post<Token>("/users/auth/login", { email, password }),

  /** GET /users/me */
  getProfile: () =>
    api.get<User>("/users/me"),

  /** GET /users/me/stats */
  getStats: () =>
    api.get<Stats>("/users/me/stats"),
};
```

### 10.3 Composant Timer — Chronomètre de speedcubing

```typescript
// src/components/timer/Timer.tsx
//
// Le chronomètre est l'élément central de l'application.
// Il fonctionne avec les touches du clavier :
// - Espace LONG (maintenu) → prêt (jaune → vert)
// - Relâcher Espace → démarre
// - Espace → arrête et enregistre le temps

import { useState, useEffect, useCallback, useRef } from "react";

type TimerState = "idle" | "ready" | "running" | "stopped";

export function Timer({ onSolve }: { onSolve: (timeMs: number) => void }) {
  const [state, setState] = useState<TimerState>("idle");
  const [timeMs, setTimeMs] = useState(0);
  const startRef = useRef<number>(0);
  const frameRef = useRef<number>(0);

  // === Animation frame pour un affichage fluide ===
  const updateTimer = useCallback(() => {
    if (startRef.current > 0) {
      setTimeMs(performance.now() - startRef.current);
      frameRef.current = requestAnimationFrame(updateTimer);
    }
  }, []);

  // === Gestion du clavier ===
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code !== "Space") return;
      e.preventDefault();

      if (state === "idle" || state === "stopped") {
        setState("ready");  // Espace maintenu → prêt
      } else if (state === "running") {
        // Arrêter le chrono
        cancelAnimationFrame(frameRef.current);
        const finalTime = performance.now() - startRef.current;
        setTimeMs(finalTime);
        setState("stopped");
        onSolve(Math.round(finalTime));  // Envoyer au parent
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code !== "Space") return;
      if (state === "ready") {
        // Relâcher → démarrer
        startRef.current = performance.now();
        setTimeMs(0);
        setState("running");
        frameRef.current = requestAnimationFrame(updateTimer);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, [state, updateTimer, onSolve]);

  // === Formatage du temps (12450 → "12.45") ===
  const formatTime = (ms: number) => {
    const seconds = ms / 1000;
    return seconds.toFixed(2);
  };

  return (
    <div className={`timer timer--${state}`}>
      <span className="timer__display">
        {formatTime(timeMs)}
      </span>
      <span className="timer__hint">
        {state === "idle" && "Appuyez sur Espace pour commencer"}
        {state === "ready" && "Relâchez pour démarrer..."}
        {state === "running" && "Appuyez sur Espace pour arrêter"}
        {state === "stopped" && "Appuyez sur Espace pour recommencer"}
      </span>
    </div>
  );
}
```

---

## 11. DevOps — Docker Compose, Makefile & Scripts

### 11.1 Workflow de développement

```mermaid
flowchart LR
    DEV["💻 Développement\n(docker compose up)"]
    TEST["🧪 Tests\n(make test)"]
    BUILD["📦 Build\n(make build)"]
    PUSH["🚀 Push\n(make push-all)"]
    DEPLOY["☸ Deploy\n(make k8s-deploy)"]
    
    DEV --> TEST --> BUILD --> PUSH --> DEPLOY
```

### 11.2 Makefile — Commandes essentielles

```makefile
# Makefile — Commandes utilitaires pour le projet Cube.com
#
# Usage :
#   make help       → Affiche toutes les commandes disponibles
#   make up         → Démarre tous les services
#   make test       → Lance tous les tests
#   make k8s-deploy → Déploie sur Kubernetes

.PHONY: help build up down logs test

DOCKER_USERNAME ?= votre-username-dockerhub
VERSION ?= latest

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build toutes les images Docker
	docker compose build

up: ## Démarre tous les services
	docker compose up -d

up-dev: ## Démarre en mode développement (hot-reload)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

down: ## Arrête tous les services
	docker compose down

test: ## Lance tous les tests
	docker compose exec user-service pytest tests/ -v
	docker compose exec learning-service pytest tests/ -v
	docker compose exec session-service pytest tests/ -v

k8s-deploy: ## Déploie sur Kubernetes (Minikube)
	kubectl apply -f k8s/base/namespace.yaml
	kubectl apply -f k8s/base/databases/ -R
	kubectl apply -f k8s/base/user-service/ -R
	kubectl apply -f k8s/base/learning-service/ -R
	kubectl apply -f k8s/base/session-service/ -R
	kubectl apply -f k8s/base/frontend/ -R
	kubectl apply -f k8s/base/gateway/ -R
```

---

## 12. Glossaire

| Terme | Définition |
|-------|-----------|
| **ACID** | Atomicity, Consistency, Isolation, Durability — propriétés d'une transaction BDD |
| **API Gateway** | Point d'entrée unique qui route les requêtes vers les microservices |
| **ASGI** | Asynchronous Server Gateway Interface — standard Python async pour le web |
| **Beanie** | ODM (Object Document Mapper) async pour MongoDB, basé sur Pydantic |
| **ClusterIP** | Type de Service K8s accessible uniquement à l'intérieur du cluster |
| **ConfigMap** | Objet K8s pour stocker de la configuration non-sensible |
| **CORS** | Cross-Origin Resource Sharing — mécanisme de sécurité navigateur |
| **Deployment** | Objet K8s qui gère le cycle de vie des Pods (replicas, rolling updates) |
| **Docker Compose** | Outil pour définir et exécuter des applications multi-conteneurs |
| **FastAPI** | Framework web Python moderne, rapide, avec validation auto et docs OpenAPI |
| **gRPC** | Framework RPC haute performance de Google, utilise Protocol Buffers |
| **Ingress** | Objet K8s qui expose des services HTTP(S) à l'extérieur du cluster |
| **JWT** | JSON Web Token — standard d'authentification stateless |
| **Lifespan** | Pattern FastAPI pour gérer le démarrage et l'arrêt de l'application |
| **Minikube** | Outil pour exécuter un cluster Kubernetes en local |
| **mTLS** | Mutual TLS — chiffrement bidirectionnel entre services |
| **Namespace** | Isolation logique des ressources dans un cluster K8s |
| **Network Policy** | Firewall K8s pour contrôler les flux réseau entre Pods |
| **ORM** | Object-Relational Mapping — correspondance objet ↔ table SQL |
| **Pod** | Plus petite unité déployable dans K8s, contient 1+ conteneur(s) |
| **Probe** | Mécanisme K8s pour vérifier la santé d'un conteneur (liveness/readiness) |
| **Protobuf** | Protocol Buffers — format de sérialisation binaire de Google |
| **RBAC** | Role-Based Access Control — contrôle d'accès par rôles |
| **ReplicaSet** | Objet K8s qui maintient un nombre stable de Pods identiques |
| **Secret** | Objet K8s pour stocker des données sensibles (chiffrées) |
| **Service (K8s)** | Abstraction réseau qui expose un ensemble de Pods via un DNS stable |
| **SQLAlchemy** | ORM Python le plus utilisé, supporte async avec AsyncSession |
| **uvicorn** | Serveur ASGI haute performance pour Python |
| **Volume** | Stockage persistant attaché à un Pod (survit aux redémarrages) |

---

> [!NOTE]
> Ce document est une **référence vivante**. Il sera mis à jour au fur et à mesure de
> l'implémentation des fonctionnalités. Les snippets de code présentés correspondent
> aux fichiers de l'arborescence du projet.
