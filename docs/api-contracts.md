# 📑 Contrats d'API & Protocoles Inter-Services — Cube.com

Ce document formalise les contrats d'interface (REST et gRPC) exposés par chaque microservice de la plateforme Cube.com, routés via la Gateway Nginx (`http://localhost:8080/api` ou `http://cube.local/api`).

---

## 1. User & Progression Service (`:8001`)

**Préfixe Gateway :** `/api/users`

### 1.1 Authentification

#### `POST /auth/register`
Crée un compte utilisateur et retourne un JWT.

- **Request Body :**
```json
{
  "username": "speedcuber42",
  "email": "cube@example.com",
  "password": "Password123!"
}
```
- **Response (201 Created) :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

#### `POST /auth/login`
Authentifie un utilisateur existant.

- **Request Body :**
```json
{
  "email": "cube@example.com",
  "password": "Password123!"
}
```
- **Response (200 OK) :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

### 1.2 Profil & Statistiques

#### `GET /me` *(Header: `Authorization: Bearer <token>`)*
- **Response (200 OK) :**
```json
{
  "id": "e7b0a88c-7f52-4752-bf6d-8888b14a6828",
  "username": "speedcuber42",
  "email": "cube@example.com",
  "avatar_url": null,
  "created_at": "2026-10-14T10:00:00Z"
}
```

#### `GET /me/stats` *(Header: `Authorization: Bearer <token>`)*
- **Response (200 OK) :**
```json
{
  "user_id": "e7b0a88c-7f52-4752-bf6d-8888b14a6828",
  "personal_best": 11450,
  "ao5": 13200.0,
  "ao12": 14150.0,
  "ao100": null,
  "total_solves": 48
}
```

---

## 2. Learning & Content Service (`:8002`)

**Préfixe Gateway :** `/api/lessons`

### 2.1 Leçons & Formules

#### `GET /lessons`
- **Query Params :** `category` *(ex: "beginner", "f2l", "oll", "pll")*
- **Response (200 OK) :**
```json
[
  {
    "id": "6524a8f902ab4c1234567890",
    "title": "Introduction à la méthode Fridrich",
    "category": "beginner",
    "difficulty": 1,
    "description": "Comprendre les 4 étapes du CFOP",
    "steps": [
      { "title": "La croix blanche", "content": "Résoudre les 4 arêtes blanches sur la face du bas..." }
    ],
    "video_url": null,
    "order": 1,
    "created_at": "2026-10-14T10:00:00Z"
  }
]
```

#### `GET /algorithms`
- **Query Params :** `category` *(ex: "PLL", "OLL", "F2L")*
- **Response (200 OK) :**
```json
[
  {
    "id": "6524a91a02ab4c1234567891",
    "name": "T-Perm",
    "category": "PLL",
    "notation": "R U R' U' R' F R2 U' R' U' R U R' F'",
    "description": "Permutation en T, échange deux coins et deux arêtes adjacents",
    "triggers": ["Phares à gauche"],
    "image_url": null,
    "created_at": "2026-10-14T10:00:00Z"
  }
]
```

### 2.2 Scrambles WCA

#### `GET /scrambles/random?length=20`
- **Response (200 OK) :**
```json
{
  "scramble": "D2 F' R2 B2 U2 L' D2 B2 F2 R' B2 D' F' L2 R2 B' U R2 F2 U",
  "length": 20,
  "case": null
}
```

---

## 3. Session & Matchmaking Service (`:8003`)

**Préfixe Gateway :** `/api/sessions`

### 3.1 Sessions Solo

#### `POST /solo/start`
- **Request Body :**
```json
{
  "user_id": "e7b0a88c-7f52-4752-bf6d-8888b14a6828",
  "scramble": "D2 F' R2 B2 U2 L' D2 B2 F2 R' B2 D' F' L2 R2 B' U R2 F2 U"
}
```
- **Response (201 Created) :**
```json
{
  "session_id": "9bc306c5-4428-4859-9941-869269cb62ea",
  "user_id": "e7b0a88c-7f52-4752-bf6d-8888b14a6828",
  "scramble": "D2 F' R2 B2 U2 L' D2 B2 F2 R' B2 D' F' L2 R2 B' U R2 F2 U",
  "started_at": "2026-10-14T10:15:30Z"
}
```

#### `POST /solo/end`
- **Request Body :**
```json
{
  "session_id": "9bc306c5-4428-4859-9941-869269cb62ea",
  "solve_time_ms": 12450
}
```
- **Response (200 OK) :**
```json
{
  "session_id": "9bc306c5-4428-4859-9941-869269cb62ea",
  "user_id": "e7b0a88c-7f52-4752-bf6d-8888b14a6828",
  "solve_time_ms": 12450,
  "scramble": "D2 F' R2 B2 U2 L' D2 B2 F2 R' B2 D' F' L2 R2 B' U R2 F2 U",
  "is_personal_best": false,
  "message": "Temps enregistré avec succès."
}
```

### 3.2 Duels & Matchmaking

#### `POST /matchmaking/join`
- **Request Body :**
```json
{
  "user_id": "e7b0a88c-7f52-4752-bf6d-8888b14a6828",
  "username": "speedcuber42",
  "rating": 1450,
  "game_mode": "ranked"
}
```
- **Response (200 OK) :**
```json
{
  "status": "matched",
  "message": "Adversaire trouvé ! Le duel va commencer.",
  "match_id": "90e23b22-8d77-4b68-b7a9-99f187a4192b",
  "scramble": "R U R' U' D R2 U' L D2 R B2 D2 R' F2 R2 D2 B2 U2"
}
```

### 3.3 WebSocket en Direct

- **URL :** `ws://cube.local/api/sessions/ws/{user_id}`
- **Protocole :** Envoi et réception de messages JSON `{"event": "timer_tick" | "solve_done", ...}` pour synchroniser les duels en face à face.

---

## 4. Contrats gRPC Inter-Services (`proto/`)

Défini dans [`proto/user.proto`](file:///proto/user.proto) :
- `rpc GetUser (GetUserRequest) returns (UserResponse);`
- `rpc ValidateToken (ValidateTokenRequest) returns (ValidateTokenResponse);`
- `rpc UpdateStats (UpdateStatsRequest) returns (StatsResponse);`

Défini dans [`proto/session.proto`](file:///proto/session.proto) :
- `rpc StartSoloSession (StartSessionRequest) returns (SessionResponse);`
- `rpc RecordSolve (RecordSolveRequest) returns (SolveResponse);`
- `rpc JoinMatchmaking (JoinMatchmakingRequest) returns (MatchResponse);`

