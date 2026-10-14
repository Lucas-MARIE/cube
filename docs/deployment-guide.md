# 🚀 Guide de Déploiement — Cube.com

Ce guide pas-à-pas vous accompagne pour tester et déployer l'application Cube.com selon les différents paliers du TP d'évaluation.

---

## 1. Démarrage Rapide en Local (Docker Compose)

Idéal pour développer et tester sans cluster Kubernetes :

```bash
# 1. Copier le fichier de variables d'environnement
cp .env.example .env

# 2. Démarrer l'ensemble des conteneurs (Frontend + 3 Services + 3 BDD + Nginx Gateway)
make up

# Ou avec le hot-reload pour le dev :
make up-dev

# 3. Vérifier les logs
make logs

# 4. Accéder à l'application
# - Frontend : http://localhost:3000
# - API Gateway : http://localhost:8080
# - Documentation Swagger User Service : http://localhost:8080/api/users/docs
# - Documentation Swagger Learning Service : http://localhost:8080/api/lessons/docs
# - Documentation Swagger Session Service : http://localhost:8080/api/sessions/docs
```

Pour éteindre les services :
```bash
make down
```

---

## 2. Déploiement Kubernetes sur Minikube (Objectifs TP)

### Étape 1 : Initialiser Minikube (Palier 10/20)

```bash
# Démarrer le cluster Minikube avec assez de CPU et mémoire
minikube start --cpus=4 --memory=6144

# Configurer le terminal pour construire les images directement dans Docker Minikube
# Sous Linux/macOS :
eval $(minikube docker-env)

# Sous Windows PowerShell :
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Construire les images Docker
docker build -t cube-user-service:latest ./services/user-service
docker build -t cube-learning-service:latest ./services/learning-service
docker build -t cube-session-service:latest ./services/session-service
docker build -t cube-frontend:latest ./frontend
```

### Étape 2 : Déployer le premier service (Palier 10/20)

```bash
# Créer le namespace
kubectl apply -f k8s/base/namespace.yaml

# Déployer PostgreSQL et User Service
kubectl apply -f k8s/base/databases/postgres-secret.yaml
kubectl apply -f k8s/base/databases/postgres-pvc.yaml
kubectl apply -f k8s/base/databases/postgres-deployment.yaml
kubectl apply -f k8s/base/databases/postgres-service.yaml

kubectl apply -f k8s/base/user-service/deployment.yaml
kubectl apply -f k8s/base/user-service/service.yaml

# Vérifier les pods
kubectl get pods -n cube
```

### Étape 3 : Activer la Gateway Ingress (Palier 12/20)

```bash
# Activer le composant ingress dans Minikube
minikube addons enable ingress

# Déployer l'Ingress Nginx
kubectl apply -f k8s/base/gateway/ingress.yaml

# Ajouter 'cube.local' à votre fichier /etc/hosts (ou Windows hosts)
# avec l'IP renvoyée par :
minikube ip
```

### Étape 4 : Déployer le deuxième et troisième service (Palier 14/20 & 16/20)

```bash
# Déployer MongoDB et Learning Service
kubectl apply -f k8s/base/databases/mongo-deployment.yaml
kubectl apply -f k8s/base/databases/mongo-service.yaml
kubectl apply -f k8s/base/learning-service/deployment.yaml
kubectl apply -f k8s/base/learning-service/service.yaml

# Déployer Redis et Session Service
kubectl apply -f k8s/base/databases/redis-deployment.yaml
kubectl apply -f k8s/base/databases/redis-service.yaml
kubectl apply -f k8s/base/session-service/deployment.yaml
kubectl apply -f k8s/base/session-service/service.yaml

# Déployer le Frontend React
kubectl apply -f k8s/base/frontend/deployment.yaml
kubectl apply -f k8s/base/frontend/service.yaml

# Vérifier que tous les pods tournent
kubectl get pods -n cube
```

### Étape 5 : Sécuriser le Cluster (Palier 18/20)

```bash
# Appliquer les permissions minimales (RBAC)
kubectl apply -f k8s/security/rbac.yaml

# Appliquer le pare-feu réseau interne (Network Policies)
kubectl apply -f k8s/security/network-policies.yaml
```

---

## 3. Déploiement en Cloud Public (Bonus 20/20)

Pour un déploiement sur Google Cloud GKE ou AWS EKS :

1. Pousser les images sur Docker Hub / Artifact Registry :
   ```bash
   DOCKER_USERNAME=monuser make push-all
   ```

2. Adapter les tags d'image dans [`k8s/overlays/prod/kustomization.yaml`](file:///k8s/overlays/prod/kustomization.yaml)

3. Déployer via Kustomize :
   ```bash
   kubectl apply -k k8s/overlays/prod
   ```

