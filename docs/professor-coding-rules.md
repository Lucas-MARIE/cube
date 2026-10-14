# 📐 Règles de Qualité & Bonnes Pratiques — Pr. Benoît Charroux
## Transposition au Projet Microservices Cube.com

Ce document formalise les règles de codage et d'ingénierie logicielle enseignées par le professeur **Benoît Charroux** ([charroux/JavaCodingRules](https://github.com/charroux/JavaCodingRules)), transposées à l'écosystème technique de **Cube.com** (Python FastAPI, TypeScript React Three.js, Docker, Kubernetes).

---

## 1. Règle n°1 : Séparation Stricte des Couches (Layering)

> **Principe du Professeur :** *"No business code in the web layer."*
> **Référence :** `WebService.java` & `MyService.java`

### Dans le cours (Java / Spring Boot) :
- Le contrôleur web (`WebService`) a une **responsabilité unique** : gérer le protocole HTTP (extraire les paramètres, appeler le service métier, retourner le code de statut et le DTO JSON).
- **Zéro calcul, zéro logique métier** dans le contrôleur : pas de boucles de calcul de moyenne, pas de manipulation directe de la collection ou de la base.
- Les données internes sont protégées : le service retourne une copie défensive (`data.stream().toList()`).
- Le service est injecté par **injection de dépendances au constructeur** (`@Autowired`).

### Transposition sur Cube.com (Python FastAPI & React) :

```python
# ❌ INTERDIT (Code métier dans la couche Web) :
@router.post("/solves")
async def record_solve(solve_data: SolveCreate, db: AsyncSession = Depends(get_db)):
    # Calcul du PB et de l'AO5 directement dans la route HTTP : INTERDIT !
    times = await db.execute(select(SolveTime.time_ms).where(...))
    pb = min(times)
    ao5 = sum(times[-5:]) / 5
    ...

# ✅ CONFORME AUX RÈGLES CHARROUX :
# 1. Service Métier pur (services/user_service.py) :
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_solve_and_compute_stats(self, user_id: UUID, solve_time_ms: int, scramble: str) -> StatsResult:
        # Toute la logique métier, calculs statistiques, validation de triche est ICI
        ...

# 2. Routeur Web HTTP (api/v1/users.py) :
@router.post("/solves", response_model=StatsResponse, status_code=status.HTTP_201_CREATED)
async def record_solve(
    data: SolveCreate,
    user_service: UserService = Depends(get_user_service),  # Injection de dépendance
):
    stats = await user_service.record_solve_and_compute_stats(data.user_id, data.time_ms, data.scramble)
    return StatsResponse.model_validate(stats)
```

**Côté Frontend (React) :**
- Le composant `Practice.tsx` ou le composant 3D Three.js n'appelle **jamais** `fetch()` ou `axios` en direct.
- On passe par `services/sessionService.ts` et un store d'état (Zustand), séparant la vue du transport réseau.

---

## 2. Règle n°2 : Journalisation Structurée & Contextuelle (Logging)

> **Principe du Professeur :** *"See line 21 at WebService.java; See line 16 at MyService.java."*
> **Référence :** SLF4J `LoggerFactory.getLogger(...)`

### Dans le cours (Java) :
- `System.out.println()` est **formellement banni**.
- Chaque classe possède son instance de logger dédiée (`LoggerFactory.getLogger(WebService.class)`).
- Les niveaux de log ont un sens précis :
  - `INFO` : événement de routage web (`logger.info("getAverage");`)
  - `ERROR` : anomalie métier ou exception (`logger.error("0 element in the list");`)

### Transposition sur Cube.com (Python) :
- `print()` est **strictement proscrit** en production.
- Utilisation du module `logging` standard avec le nom du module `__name__` :

```python
import logging

# Logger contextualisé par module
logger = logging.getLogger(__name__)

# Dans la couche Web :
logger.info("Handling solve submission for user %s", user_id)

# Dans la couche Service / Métier :
logger.error("Scramble invalid or tampering detected for solve_id=%s", solve_id)
```

- En conteneur Docker / Kubernetes, les logs sortent au format **JSON structuré** sur stdout/stderr pour être agrégés par Fluentbit, Prometheus et Grafana/Loki.

---

## 3. Règle n°3 : Gestion Précise des Exceptions & Codes HTTP

> **Principe du Professeur :** *"Exception handling with HttpStatus code and message."*
> **Référence :** `DataException.java` annoté avec `@ResponseStatus(HttpStatus.EXPECTATION_FAILED)`
> **Configuration obligatoire :** `server.error.include-message=always` dans `application.properties`

### Dans le cours (Java) :
- Les exceptions métier étendent `Exception` et sont mappées à un code HTTP explicite.
- Le message d'erreur précis doit **impérativement être transmis au client** (d'où l'activation obligatoire de `include-message=always`, sans laquelle Spring masque le message pour raisons de sécurité).

### Transposition sur Cube.com (FastAPI) :
FastAPI masque parfois les détails internes s'ils ne sont pas explicitement modélisés. Nous transposons la règle avec des exceptions de domaine typées et un gestionnaire global :

```python
# app/exceptions/domain.py
class CubeDomainException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class InvalidScrambleException(CubeDomainException):
    def __init__(self, message: str = "Format de mélange non conforme aux règles WCA"):
        super().__init__(message=message, status_code=422)

# app/main.py
@app.exception_handler(CubeDomainException)
async def domain_exception_handler(request: Request, exc: CubeDomainException):
    logger.error("Exception domaine: %s (HTTP %d)", exc.message, exc.status_code)
    # Respect strict de la consigne du prof : le message DOIT être inclus dans le JSON retourné
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "status_code": exc.status_code},
    )
```

---

## 4. Règle n°4 : Auto-documentation Contractuelle OpenAPI (Swagger)

> **Principe du Professeur :** *"Open API documentation (Swagger) : http://localhost:8080/swagger-ui/index.html"*
> **Référence :** `springdoc-openapi-starter-webmvc-ui`

### Dans le cours (Java) :
- Les API REST doivent être **auto-documentées**, interactives et contractuelles.

### Transposition sur Cube.com :
- FastAPI génère nativement la spécification OpenAPI v3.
- Chaque microservice expose :
  - Swagger UI : `http://localhost:8001/docs` (User), `:8002/docs` (Learning), `:8003/docs` (Session).
  - Via l'API Gateway : `http://cube.local/api/users/docs`, `http://cube.local/api/lessons/docs`, etc.
- Tous les schémas Pydantic définissent des types stricts, des descriptions et des exemples (`examples=[...]`).

---

## 5. Règle n°5 : Isolation des Tests Unitaires (Fixtures)

> **Principe du Professeur :** *"Unit testing with JUnit 5 documentation."*
> **Référence :** `MyDataTest.java` avec `@BeforeEach public void init()`

### Dans le cours (Java) :
- Les tests unitaires testent une unité de logique isolée.
- La méthode `@BeforeEach` réinitialise l'état avant chaque test pour éviter tout effet de bord ou fuite d'état mutable.

### Transposition sur Cube.com (Pytest) :
- Utilisation de fixtures Pytest `autouse=True` dans `conftest.py` pour isoler chaque test :

```python
# tests/conftest.py
@pytest.fixture(autouse=True)
async def reset_state():
    """Équivalent de @BeforeEach : réinitialise les mocks et la BDD mémoire."""
    yield
    # Cleanup après chaque test
```

---

## 6. Règle n°6 : Tests de Tranche Web & Mocking (Pattern Mockito)

> **Principe du Professeur :** *"Web tier testing with MockMvc and Mockito."*
> **Référence :** `@WebMvcTest(WebService.class)` + `@MockBean private MyService myService`

### Dans le cours (Java) :
- On teste la couche web **sans démarrer la vraie base de données**.
- Le service métier est simulé par un **Mock** (`when(myService.average()).thenReturn(1)`).
- Le test valide :
  - Le code HTTP (`status().isOk()`)
  - Le type MIME (`MediaType.APPLICATION_JSON`)
  - La structure JSON (`jsonPath("$", hasSize(1))`, `jsonPath("$[0].i", equalTo(1))`)

### Transposition sur Cube.com (FastAPI Slice Testing) :

```python
# services/session-service/tests/test_api_mocked.py
import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.timer_service import TimerService

@pytest.mark.asyncio
async def test_session_endpoint_with_mock():
    # 1. Création du Mock (équivalent Mockito @MockBean)
    mock_timer_service = AsyncMock(spec=TimerService)
    mock_timer_service.create_session.return_value = {
        "session_id": "test-uuid",
        "scramble": "R U R' U'",
        "user_id": "usr-1"
    }

    # 2. Injection du Mock via dependency_overrides
    app.dependency_overrides[get_timer_service] = lambda: mock_timer_service

    # 3. Test HTTP (équivalent MockMvc.perform())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/solo/start", json={"user_id": "usr-1", "scramble": "R U R' U'"})

    # 4. Assertions strictes sur le contrat HTTP et le JSON
    assert response.status_code == 201
    assert response.json()["session_id"] == "test-uuid"
    mock_timer_service.create_session.assert_called_once()

    app.dependency_overrides.clear()
```

---

## 7. Règle n°7 : Automatisation des Builds & Métriques de Couverture

> **Principe du Professeur :** *"Launch the tests: ./gradlew build. Check results in build/reports/test/tests/index.html"* (et JaCoCo / GitHub Actions dans ses cours DevOps).

### Transposition sur Cube.com :
- **Makefile unifié** : commande unique `make test` pour exécuter la totalité des suites de tests de tous les microservices et du frontend.
- **Rapports de couverture** : génération d'un rapport HTML de couverture de code (équivalent JaCoCo) avec `pytest --cov=app --cov-report=html`.
- **Validation continue** : intégration dans un pipeline GitHub Actions bloquant en cas d'échec ou de couverture insuffisante.

---

## 📋 Synthèse pour l'Évaluation du TP

| Règle Pr. Charroux | Implémentation dans Cube.com | Fichier de Référence |
| :--- | :--- | :--- |
| **Layering** | Découpage strict Routeurs (`api/v1`) $\rightarrow$ Services métier (`services/`) $\rightarrow$ Modèles ORM (`models/`). | [`user-service/app/services/user_service.py`](file:///services/user-service/app/services/user_service.py) |
| **Logging** | Logger standard `logging.getLogger(__name__)`, aucun `print()`. | Tous les modules `app/` |
| **Exceptions HTTP** | Exceptions typées avec status HTTP explicites et messages détaillés préservés. | `app/exceptions/` |
| **OpenAPI / Swagger** | OpenAPI v3 documenté et interactif sur chaque service et via la gateway Nginx. | `http://localhost:8080/api/users/docs` |
| **Tests Isolés** | Fixtures `pytest` isolées par test, base SQLite/fakeredis en mémoire. | `tests/conftest.py` |
| **Mocking Web Tier** | Tests HTTP de tranche avec `httpx` et `dependency_overrides` (équivalent Mockito). | `tests/test_*.py` |
| **Build & Quality** | `make test`, `make build`, K8s liveness/readiness probes. | [`Makefile`](file:///Makefile) |

