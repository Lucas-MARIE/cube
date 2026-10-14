"""Tests unitaires pour le service d'apprentissage."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Vérifie que l'endpoint de santé répond correctement."""
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy", "service": "learning-service"}


@pytest.mark.asyncio
async def test_random_scramble(client):
    """Vérifie la génération d'un scramble WCA."""
    res = await client.get("/scrambles/random")
    assert res.status_code == 200
    data = res.json()
    assert "scramble" in data
    assert data["length"] == 20
    moves = data["scramble"].split()
    assert len(moves) == 20

