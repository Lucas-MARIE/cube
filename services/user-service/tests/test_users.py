"""Tests unitaires pour les endpoints de user-service."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Vérifie que l'endpoint /health répond correctement."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "user-service"}


import uuid


@pytest.mark.asyncio
async def test_register_and_login(client):
    """Teste le cycle complet d'inscription puis connexion."""
    uid = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"user_{uid}",
        "email": f"user_{uid}@cube.com",
        "password": "Password123!",
    }

    # Inscription
    reg_response = await client.post("/v1/auth/register", json=user_data)
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert data["username"] == user_data["username"]
    assert "id" in data

    # Connexion
    login_response = await client.post(
        "/v1/auth/login",
        json={"email": user_data["email"], "password": "Password123!"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data

