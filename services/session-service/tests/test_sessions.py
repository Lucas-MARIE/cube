"""Tests unitaires pour le service de sessions et chronomètre."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Vérifie l'endpoint /health de session-service."""
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy", "service": "session-service"}


@pytest.mark.asyncio
async def test_start_and_end_session(client):
    """Teste le cycle de démarrage et complétion d'un solve."""
    start_payload = {
        "user_id": "usr-12345",
        "scramble": "R U R' U' F' U2 F",
    }
    start_res = await client.post("/solo/start", json=start_payload)
    assert start_res.status_code == 201
    start_data = start_res.json()
    assert "session_id" in start_data
    session_id = start_data["session_id"]

    # Terminer la session avec un temps de 14.52s (14520ms)
    end_payload = {
        "session_id": session_id,
        "solve_time_ms": 14520,
    }
    end_res = await client.post("/solo/end", json=end_payload)
    assert end_res.status_code == 200
    end_data = end_res.json()
    assert end_data["solve_time_ms"] == 14520
    assert end_data["session_id"] == session_id

