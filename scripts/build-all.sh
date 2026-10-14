#!/usr/bin/env bash
# =============================================================================
# build-all.sh - Construction de toutes les images Docker du projet Cube
# =============================================================================
# Ce script construit les images Docker pour tous les microservices.
# Usage : ./scripts/build-all.sh [TAG]
#   TAG : Tag optionnel pour les images (défaut: latest)
#
# Exemples :
#   ./scripts/build-all.sh          # Build avec le tag 'latest'
#   ./scripts/build-all.sh v1.0.0   # Build avec le tag 'v1.0.0'
#   ./scripts/build-all.sh dev      # Build avec le tag 'dev'
# =============================================================================

set -euo pipefail

# --- Configuration ---
# Tag des images (argument ou 'latest' par défaut)
TAG="${1:-latest}"
# Répertoire racine du projet
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Fonctions utilitaires ---
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

# --- Liste des services à construire ---
# Format : "nom_image:chemin_du_Dockerfile"
SERVICES=(
    "cube-user-service:${PROJECT_ROOT}/services/user-service"
    "cube-learning-service:${PROJECT_ROOT}/services/learning-service"
    "cube-session-service:${PROJECT_ROOT}/services/session-service"
    "cube-frontend:${PROJECT_ROOT}/frontend"
)

# --- Vérification des prérequis ---
if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé ou pas dans le PATH"
    exit 1
fi

# --- Construction des images ---
echo ""
echo "============================================="
echo "  🧊 Cube - Construction des images Docker"
echo "  Tag: ${TAG}"
echo "============================================="
echo ""

FAILED=0
BUILT=0

for service in "${SERVICES[@]}"; do
    # Extraction du nom et du chemin
    IMAGE_NAME="${service%%:*}"
    BUILD_PATH="${service##*:}"

    log_info "Construction de ${IMAGE_NAME}:${TAG}..."

    # Vérifier que le Dockerfile existe
    if [ ! -f "${BUILD_PATH}/Dockerfile" ]; then
        log_warn "Dockerfile non trouvé dans ${BUILD_PATH}, ignoré"
        continue
    fi

    # Construction de l'image
    if docker build \
        -t "${IMAGE_NAME}:${TAG}" \
        -f "${BUILD_PATH}/Dockerfile" \
        --label "org.opencontainers.image.source=https://github.com/cube-project/cube" \
        --label "org.opencontainers.image.version=${TAG}" \
        --label "org.opencontainers.image.created=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        "${BUILD_PATH}"; then
        log_success "${IMAGE_NAME}:${TAG} construit avec succès"
        BUILT=$((BUILT + 1))
    else
        log_error "Échec de la construction de ${IMAGE_NAME}:${TAG}"
        FAILED=$((FAILED + 1))
    fi
    echo ""
done

# --- Résumé ---
echo "============================================="
echo "  📊 Résumé de la construction"
echo "============================================="
echo -e "  ${GREEN}Réussis : ${BUILT}${NC}"
echo -e "  ${RED}Échoués : ${FAILED}${NC}"
echo "============================================="

if [ ${FAILED} -gt 0 ]; then
    log_error "Certaines images n'ont pas pu être construites"
    exit 1
fi

log_success "Toutes les images ont été construites avec succès !"
