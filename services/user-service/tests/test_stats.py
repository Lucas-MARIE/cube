"""Tests de tranche web et mocking (Pattern Mockito / @WebMvcTest).

Conforme à la règle 6 du Pr. Charroux : tester le contrat HTTP
en bouchonnant (mocking) la couche service.
"""

from unittest.mock import AsyncMock
import pytest
from app.main import app
from app.services.stats_service import StatsService
from app.api.v1.stats import get_stats_service
from app.services.auth_service import get_current_user
from app.models.user import User
import uuid


@pytest.fixture
def mock_current_user():
    user = User(
        id=uuid.uuid4(),
        username="speedcuber_mock",
        email="mock@cube.com",
        hashed_password="hash",
    )
    return user


@pytest.mark.asyncio
async def test_get_stats_slice_with_mock(client, mock_current_user):
    """Test HTTP isolé avec mock du StatsService (équivalent @MockBean de Spring)."""
    # 1. Préparation du Mock (équivalent when(service.get_user_stats()).thenReturn(...))
    mock_stats_service = AsyncMock(spec=StatsService)
    mock_stats_service.get_user_stats.return_value = {
        "personal_best": 9450,
        "ao5": 11200.0,
        "ao12": 12400.0,
        "ao100": None,
        "total_solves": 42,
    }

    # 2. Injection des dépendances mockées
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    app.dependency_overrides[get_stats_service] = lambda: mock_stats_service

    try:
        # 3. Exécution de la requête HTTP
        response = await client.get("/v1/stats/me/stats")

        # 4. Vérification du contrat HTTP et structure JSON (équivalent MockMvc andExpect)
        assert response.status_code == 200
        data = response.json()
        assert data["personal_best"] == 9450
        assert data["ao5"] == 11200.0
        assert data["total_solves"] == 42

        # 5. Vérification de l'appel (équivalent verify(service).get_user_stats(...))
        mock_stats_service.get_user_stats.assert_called_once_with(mock_current_user.id)
    finally:
        app.dependency_overrides.clear()

