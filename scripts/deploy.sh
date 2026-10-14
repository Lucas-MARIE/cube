#!/usr/bin/env bash
# =============================================================================
# deploy.sh - Déploiement de toutes les ressources Kubernetes
# =============================================================================
# Ce script déploie les ressources K8s dans l'ordre correct :
#   1. Namespace (espace de noms)
#   2. RBAC (comptes de service et rôles)
#   3. Secrets et ConfigMaps
#   4. Bases de données (PostgreSQL, MongoDB, Redis)
#   5. Services applicatifs (user, learning, session)
#   6. Frontend
#   7. Gateway (Ingress)
#   8. Politiques de sécurité réseau
#
# Usage : ./scripts/deploy.sh [ENVIRONMENT]
#   ENVIRONMENT : 'dev' ou 'prod' (défaut: dev)
#
# Exemples :
#   ./scripts/deploy.sh          # Déploie en mode dev
#   ./scripts/deploy.sh dev      # Déploie en mode dev
#   ./scripts/deploy.sh prod     # Déploie en mode production
# =============================================================================

set -euo pipefail

# --- Configuration ---
ENV="${1:-dev}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
K8S_DIR="${PROJECT_ROOT}/k8s"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERREUR]${NC} $1"; }
log_step() { echo -e "\n${CYAN}━━━ $1 ━━━${NC}"; }

# --- Vérification des prérequis ---
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl n'est pas installé ou pas dans le PATH"
    exit 1
fi

# Vérifier la connexion au cluster
if ! kubectl cluster-info &> /dev/null; then
    log_error "Impossible de se connecter au cluster Kubernetes"
    log_info "Vérifiez votre kubeconfig ou lancez Minikube avec: minikube start"
    exit 1
fi

echo ""
echo "============================================="
echo "  🧊 Cube - Déploiement Kubernetes"
echo "  Environnement: ${ENV}"
echo "  Cluster: $(kubectl config current-context)"
echo "============================================="
echo ""

# --- Confirmation en production ---
if [ "${ENV}" = "prod" ]; then
    log_warn "⚠️  Vous êtes sur le point de déployer en PRODUCTION"
    read -p "Continuer ? (yes/no): " CONFIRM
    if [ "${CONFIRM}" != "yes" ]; then
        log_info "Déploiement annulé"
        exit 0
    fi
fi

# --- Étape 1 : Namespace ---
log_step "1/8 - Création du namespace"
kubectl apply -f "${K8S_DIR}/base/namespace.yaml"
log_success "Namespace 'cube' créé"

# --- Étape 2 : RBAC ---
log_step "2/8 - Configuration RBAC"
kubectl apply -f "${K8S_DIR}/security/rbac.yaml"
log_success "ServiceAccounts, Roles et RoleBindings créés"

# --- Étape 3 : Secrets ---
log_step "3/8 - Déploiement des secrets"
kubectl apply -f "${K8S_DIR}/base/databases/postgres-secret.yaml"
log_success "Secrets déployés"

# --- Étape 4 : Bases de données ---
log_step "4/8 - Déploiement des bases de données"

# PostgreSQL
log_info "Déploiement de PostgreSQL..."
kubectl apply -f "${K8S_DIR}/base/databases/postgres-pvc.yaml"
kubectl apply -f "${K8S_DIR}/base/databases/postgres-deployment.yaml"
kubectl apply -f "${K8S_DIR}/base/databases/postgres-service.yaml"
log_success "PostgreSQL déployé"

# MongoDB
log_info "Déploiement de MongoDB..."
kubectl apply -f "${K8S_DIR}/base/databases/mongo-deployment.yaml"
kubectl apply -f "${K8S_DIR}/base/databases/mongo-service.yaml"
log_success "MongoDB déployé"

# Redis
log_info "Déploiement de Redis..."
kubectl apply -f "${K8S_DIR}/base/databases/redis-deployment.yaml"
kubectl apply -f "${K8S_DIR}/base/databases/redis-service.yaml"
log_success "Redis déployé"

# Attendre que les bases de données soient prêtes
log_info "Attente de la disponibilité des bases de données (60s max)..."
kubectl wait --for=condition=available deployment/postgres -n cube --timeout=60s 2>/dev/null || log_warn "PostgreSQL pas encore prêt"
kubectl wait --for=condition=available deployment/mongo -n cube --timeout=60s 2>/dev/null || log_warn "MongoDB pas encore prêt"
kubectl wait --for=condition=available deployment/redis -n cube --timeout=60s 2>/dev/null || log_warn "Redis pas encore prêt"

# --- Étape 5 : Services applicatifs ---
log_step "5/8 - Déploiement des services applicatifs"

# User Service
log_info "Déploiement du user-service..."
kubectl apply -f "${K8S_DIR}/base/user-service/deployment.yaml"
kubectl apply -f "${K8S_DIR}/base/user-service/service.yaml"
log_success "User service déployé"

# Learning Service
log_info "Déploiement du learning-service..."
kubectl apply -f "${K8S_DIR}/base/learning-service/deployment.yaml"
kubectl apply -f "${K8S_DIR}/base/learning-service/service.yaml"
log_success "Learning service déployé"

# Session Service
log_info "Déploiement du session-service..."
kubectl apply -f "${K8S_DIR}/base/session-service/deployment.yaml"
kubectl apply -f "${K8S_DIR}/base/session-service/service.yaml"
log_success "Session service déployé"

# --- Étape 6 : Frontend ---
log_step "6/8 - Déploiement du frontend"
kubectl apply -f "${K8S_DIR}/base/frontend/deployment.yaml"
kubectl apply -f "${K8S_DIR}/base/frontend/service.yaml"
log_success "Frontend déployé"

# --- Étape 7 : Gateway (Ingress) ---
log_step "7/8 - Configuration de l'Ingress Gateway"
kubectl apply -f "${K8S_DIR}/base/gateway/ingress.yaml"
log_success "Ingress configuré"

# --- Étape 8 : Network Policies ---
log_step "8/8 - Application des politiques réseau"
kubectl apply -f "${K8S_DIR}/security/network-policies.yaml"
log_success "Network policies appliquées"

# --- Résumé ---
echo ""
echo "============================================="
echo "  ✅ Déploiement terminé avec succès !"
echo "============================================="
echo ""
log_info "Vérification de l'état des pods :"
echo ""
kubectl get pods -n cube -o wide
echo ""
log_info "Services exposés :"
kubectl get svc -n cube
echo ""
log_info "Ingress :"
kubectl get ingress -n cube
echo ""

# Instructions post-déploiement
if [ "${ENV}" = "dev" ]; then
    echo "============================================="
    echo "  📝 Prochaines étapes (développement)"
    echo "============================================="
    echo "  1. Ajouter 'cube.local' à /etc/hosts :"
    echo "     echo \"\$(minikube ip) cube.local\" | sudo tee -a /etc/hosts"
    echo "  2. Accéder à l'application : http://cube.local"
    echo "  3. Vérifier les logs : kubectl logs -f deployment/<service> -n cube"
    echo "============================================="
fi
