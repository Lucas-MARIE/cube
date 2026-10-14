"""Tests unitaires pour les endpoints de user-service."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Vérifie que l'endpoint /health répond correctement."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "user-service"}


@pytest.mark.asyncio
async def test_register_and_login(client):
    """Teste le cycle complet d'inscription puis connexion."""
    user_data = {
        "username": "testcuber",
        "email": "test@cube.com",
        "password": "Password123!",
    }

    # Inscription
    reg_response = await client.post("/auth/register", json=user_data)
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Connexion
    login_response = await client.post(
        "/auth/login",
        json={"email": "test@cube.com", "password": "Password123!"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data

