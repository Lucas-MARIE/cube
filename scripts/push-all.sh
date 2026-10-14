#!/usr/bin/env bash
# =============================================================================
# push-all.sh - Push de toutes les images Docker vers Docker Hub
# =============================================================================
# Ce script pousse les images Docker vers Docker Hub (ou un autre registre).
# Usage : ./scripts/push-all.sh [TAG]
#   TAG : Tag optionnel pour les images (défaut: latest)
#
# Variables d'environnement requises :
#   DOCKER_USERNAME : Nom d'utilisateur Docker Hub
#
# Exemples :
#   DOCKER_USERNAME=monuser ./scripts/push-all.sh
#   DOCKER_USERNAME=monuser ./scripts/push-all.sh v1.0.0
# =============================================================================

set -euo pipefail

# --- Configuration ---
TAG="${1:-latest}"
# Le nom d'utilisateur Docker Hub doit être défini
DOCKER_USERNAME="${DOCKER_USERNAME:?Erreur: DOCKER_USERNAME n'est pas défini. Utilisez: export DOCKER_USERNAME=votre_username}"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_error() { echo -e "${RED}[ERREUR]${NC} $1"; }

# --- Liste des images à pousser ---
IMAGES=(
    "cube-user-service"
    "cube-learning-service"
    "cube-session-service"
    "cube-frontend"
)

# --- Vérification de la connexion Docker Hub ---
if ! docker info &> /dev/null; then
    log_error "Le daemon Docker n'est pas en cours d'exécution"
    exit 1
fi

# Vérifier la connexion à Docker Hub
log_info "Vérification de la connexion à Docker Hub..."
if ! docker login --username "${DOCKER_USERNAME}" 2>/dev/null; then
    log_error "Impossible de se connecter à Docker Hub. Exécutez 'docker login' d'abord."
    exit 1
fi

# --- Push des images ---
echo ""
echo "============================================="
echo "  🧊 Cube - Push des images Docker"
echo "  Registry: docker.io/${DOCKER_USERNAME}"
echo "  Tag: ${TAG}"
echo "============================================="
echo ""

FAILED=0
PUSHED=0

for image in "${IMAGES[@]}"; do
    REMOTE_IMAGE="${DOCKER_USERNAME}/${image}:${TAG}"

    log_info "Tagging ${image}:${TAG} -> ${REMOTE_IMAGE}..."
    docker tag "${image}:${TAG}" "${REMOTE_IMAGE}"

    log_info "Push de ${REMOTE_IMAGE}..."
    if docker push "${REMOTE_IMAGE}"; then
        log_success "${REMOTE_IMAGE} poussé avec succès"
        PUSHED=$((PUSHED + 1))
    else
        log_error "Échec du push de ${REMOTE_IMAGE}"
        FAILED=$((FAILED + 1))
    fi
    echo ""
done

# --- Résumé ---
echo "============================================="
echo "  📊 Résumé du push"
echo "============================================="
echo -e "  ${GREEN}Réussis : ${PUSHED}${NC}"
echo -e "  ${RED}Échoués : ${FAILED}${NC}"
echo "============================================="

if [ ${FAILED} -gt 0 ]; then
    log_error "Certaines images n'ont pas pu être poussées"
    exit 1
fi

log_success "Toutes les images ont été poussées avec succès !"
