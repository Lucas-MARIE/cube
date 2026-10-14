#!/usr/bin/env bash
# =============================================================================
# setup-minikube.sh - Configuration de Minikube pour le développement local
# =============================================================================
# Ce script configure un cluster Minikube optimisé pour le projet Cube :
#   - Alloue suffisamment de ressources (CPU, RAM)
#   - Active les addons nécessaires (ingress, metrics-server)
#   - Construit les images Docker dans le daemon Minikube
#
# Usage : ./scripts/setup-minikube.sh
#
# Prérequis :
#   - Minikube installé (https://minikube.sigs.k8s.io/docs/start/)
#   - Docker installé
#   - kubectl installé
# =============================================================================

set -euo pipefail

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Ressources allouées à Minikube
MINIKUBE_CPUS=4
MINIKUBE_MEMORY=8192  # 8 Go de RAM
MINIKUBE_DISK="30g"   # 30 Go de disque
MINIKUBE_DRIVER="docker"  # Utiliser Docker comme driver

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
echo ""
echo "============================================="
echo "  🧊 Cube - Configuration Minikube"
echo "============================================="
echo ""

log_step "Vérification des prérequis"

# Vérifier Minikube
if ! command -v minikube &> /dev/null; then
    log_error "Minikube n'est pas installé"
    log_info "Installation : https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi
log_success "Minikube trouvé : $(minikube version --short 2>/dev/null || echo 'version inconnue')"

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé"
    exit 1
fi
log_success "Docker trouvé : $(docker --version)"

# Vérifier kubectl
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl n'est pas installé"
    exit 1
fi
log_success "kubectl trouvé : $(kubectl version --client --short 2>/dev/null || echo 'version inconnue')"

# --- Étape 1 : Démarrage de Minikube ---
log_step "1/4 - Démarrage de Minikube"

# Vérifier si Minikube tourne déjà
if minikube status &> /dev/null; then
    log_warn "Minikube est déjà en cours d'exécution"
    read -p "Voulez-vous le redémarrer ? (yes/no): " RESTART
    if [ "${RESTART}" = "yes" ]; then
        log_info "Suppression du cluster existant..."
        minikube delete
    else
        log_info "Utilisation du cluster existant"
    fi
fi

# Démarrer Minikube avec les ressources adéquates
if ! minikube status &> /dev/null; then
    log_info "Démarrage de Minikube avec ${MINIKUBE_CPUS} CPUs, ${MINIKUBE_MEMORY}Mo RAM..."
    minikube start \
        --cpus="${MINIKUBE_CPUS}" \
        --memory="${MINIKUBE_MEMORY}" \
        --disk-size="${MINIKUBE_DISK}" \
        --driver="${MINIKUBE_DRIVER}" \
        --kubernetes-version=stable \
        --container-runtime=docker \
        --addons=default-storageclass,storage-provisioner

    log_success "Minikube démarré avec succès"
else
    log_success "Minikube est déjà en cours d'exécution"
fi

# --- Étape 2 : Activation des addons ---
log_step "2/4 - Activation des addons"

# Ingress Controller (Nginx)
log_info "Activation de l'addon Ingress..."
minikube addons enable ingress
log_success "Ingress activé"

# Metrics Server (pour l'autoscaling)
log_info "Activation du Metrics Server..."
minikube addons enable metrics-server
log_success "Metrics Server activé"

# Dashboard (optionnel mais utile pour le monitoring)
log_info "Activation du Dashboard Kubernetes..."
minikube addons enable dashboard
log_success "Dashboard activé"

# Afficher les addons actifs
log_info "Addons actifs :"
minikube addons list | grep STATUS -A 100 | grep enabled

# --- Étape 3 : Construction des images dans Minikube ---
log_step "3/4 - Construction des images dans Minikube"

# Configurer le shell pour utiliser le daemon Docker de Minikube
# Cela permet de construire les images directement dans Minikube
# sans avoir besoin de les pousser vers un registre
log_info "Configuration du daemon Docker de Minikube..."
log_info "Exécution de: eval \$(minikube docker-env)"
eval $(minikube docker-env)

# Construire les images
log_info "Construction des images Docker dans Minikube..."
if [ -f "${PROJECT_ROOT}/scripts/build-all.sh" ]; then
    bash "${PROJECT_ROOT}/scripts/build-all.sh" dev
    log_success "Images construites dans Minikube"
else
    log_warn "Le script build-all.sh n'a pas été trouvé"
    log_info "Les images seront construites manuellement"
fi

# Vérifier les images construites
log_info "Images disponibles dans Minikube :"
docker images | grep cube || log_warn "Aucune image 'cube' trouvée"

# --- Étape 4 : Vérification finale ---
log_step "4/4 - Vérification du cluster"

# Informations du cluster
log_info "Informations du cluster :"
kubectl cluster-info
echo ""

# Nœuds du cluster
log_info "Nœuds :"
kubectl get nodes -o wide
echo ""

# IP de Minikube
MINIKUBE_IP=$(minikube ip)
log_info "IP de Minikube : ${MINIKUBE_IP}"

# --- Résumé ---
echo ""
echo "============================================="
echo "  ✅ Minikube configuré avec succès !"
echo "============================================="
echo ""
echo "  Prochaines étapes :"
echo ""
echo "  1. Déployer les services :"
echo "     ./scripts/deploy.sh dev"
echo ""
echo "  2. Ajouter l'entrée DNS locale :"
echo "     echo \"${MINIKUBE_IP} cube.local\" | sudo tee -a /etc/hosts"
echo ""
echo "  3. Accéder à l'application :"
echo "     http://cube.local"
echo ""
echo "  4. Ouvrir le dashboard Kubernetes :"
echo "     minikube dashboard"
echo ""
echo "  5. Voir les logs d'un service :"
echo "     kubectl logs -f deployment/user-service -n cube"
echo ""
echo "  Commandes utiles :"
echo "     minikube status          # État du cluster"
echo "     minikube stop            # Arrêter le cluster"
echo "     minikube delete          # Supprimer le cluster"
echo "     minikube tunnel          # Exposer les LoadBalancer"
echo ""
echo "============================================="
