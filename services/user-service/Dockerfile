# =============================================================================
# Cube.com - User Service | Dockerfile de production
# Build multi-stage pour une image optimisée et sécurisée
# =============================================================================

# --- Étape 1 : Builder ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Installer les dépendances système pour la compilation
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Étape 2 : Runtime ---
FROM python:3.12-slim AS runtime

LABEL maintainer="Cube.com Team"
LABEL service="user-service"

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r cube && useradd -r -g cube -s /bin/false cube

# Installer les dépendances runtime uniquement
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python depuis le builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Copier le code source
COPY . .

# Changer le propriétaire des fichiers
RUN chown -R cube:cube /app

# Basculer vers l'utilisateur non-root
USER cube

# Exposer le port du service
EXPOSE 8001

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health')" || exit 1

# Lancer le serveur avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
