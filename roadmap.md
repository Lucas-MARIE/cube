Ton idée de plateforme autour du Rubik's Cube, façon "Chess.com", est excellente et se prête particulièrement bien à une architecture en microservices ! Le découpage des fonctionnalités en domaines distincts est naturel et permet de bien répondre aux exigences de ton TP.

Voici une analyse de l'énoncé du TP suivie d'une proposition d'architecture microservices pour ton projet.

### Analyse de l'énoncé du TP

L'énoncé du projet "Projet 2025.docx" met l'accent sur la maîtrise des technologies d'infrastructure et de déploiement, plus que sur la complexité métier de l'application. Voici les points clés à retenir :

**Contraintes et Technologies Imposées :**

* **Architecture :** Microservices.


* **Communication :** REST et/ou gRPC (gRPC est un bonus).


* **Conteneurisation & Orchestration :** Docker et Kubernetes sont obligatoires.


* **Langages :** Libres (tu as choisi Python pour le back et React pour le front, ce qui est parfait).


* **Front-end :** Optionnel mais recommandé (React est un excellent choix).


* **Organisation :** Travail en binôme.



**Barème et Étapes (très important pour prioriser le travail) :**
Le TP est évalué selon des paliers d'intégration technologique :

1. **10/20 : Un seul service en local.** Coder une mini-application, créer l'image Docker, la publier sur Docker Hub, et créer un déploiement et un service Kubernetes.


2. **12/20 : Ajouter une Gateway.** Utiliser un Ingress ou un Service Mesh (comme Istio) en local.


3. **14/20 : Ajouter un deuxième service.** Créer un second service, le conteneuriser, le déployer sur Kubernetes, et faire communiquer les deux services entre eux, idéalement via la Gateway ou le Service Mesh.


4. **16/20 : Ajouter une base de données.** Intégrer une BDD (in-memory, MySQL, PostgreSQL, etc.) pour la persistance des données.


5. **18/20 : Sécuriser le cluster.** Implémenter des RBAC Kubernetes, du mTLS via le Service Mesh, ou sécuriser la Registry Docker.


6. **20/20 (Bonus) : Déploiement Cloud et/ou Sécurité avancée.** Déployer l'infrastructure sur un cloud public (GCP, AWS, Azure, etc.).



**Livrables :**

* Un mini rapport explicatif avec des captures d'écran (pour montrer ce qui a été fait et ce qui est attendu).


* Captures d'écran individuelles des Google Labs.


* Le code source hébergé sur un dépôt Git (Github ou Gitlab).



**Critères d'évaluation (par ordre d'importance) :**

1. Intégration technologique (Web Services, Docker, Kubernetes…).


2. Codage.


3. Fonctionnalités.


4. Présentation (Front office - CSS).



**Conclusion sur le TP :** Ton objectif principal doit être de mettre en place l'infrastructure (Docker, Kubernetes, Gateway, BDD) avec un ou deux microservices simples. Les fonctionnalités complexes (le cube 3D, le matchmaking en temps réel) viendront dans un second temps, une fois l'architecture de base validée.

---

### Proposition d'Architecture Microservices pour "Cube.com"

Puisque le TP valorise l'intégration technologique (jusqu'à 14/20 pour deux services communicants via une gateway), voici un découpage minimaliste mais évolutif.

#### 1. Architecture Front-end (React)

* **Le Client "CubeApp" (React) :**
* S'occupe de l'interface utilisateur.
* Intègre le composant du cube 3D (par exemple avec Three.js ou React Three Fiber).
* Gère la logique d'affichage des fiches (PLL, OLL) et des leçons.
* Gère les inputs clavier (bindings configurables) pour tourner le cube.
* *Note : Le front-end communiquera avec les microservices via une API Gateway.*



#### 2. Découpage des Microservices (Python / FastAPI ou Flask)

Voici une proposition de découpage en 3 microservices principaux, ce qui est parfait pour viser les 14/20 ou 16/20 du TP.

**Service 1 : `User & Progression Service` (Le cœur de la gamification)**

* **Responsabilités :**
* Gestion des comptes utilisateurs (inscription, connexion).
* Gestion des profils (pseudo, avatar).
* Suivi des statistiques de base (PB - Personal Best, AV3, AV5, AV12).
* Gestion des badges et succès déverrouillés.


* **Base de données :** PostgreSQL ou MongoDB (pour stocker les profils, les temps et les succès).
* **Justification pour le TP :** C'est un excellent premier service à développer (objectif 10/20) car il est classique et facile à tester (CRUD sur des utilisateurs).

**Service 2 : `Learning & Content Service` (Le contenu statique et les problèmes)**

* **Responsabilités :**
* Fournir le contenu des leçons (Fridrich débutant, avancé, F2L, OLL, PLL).
* Générer ou fournir des "scrambles" (mélanges) spécifiques pour les problèmes (ex: scramble pour un cas F2L précis ou une croix spécifique).
* Fournir les fiches à imprimer (génération de PDF ou liens vers des ressources statiques).


* **Base de données :** Une base NoSQL documentaire (comme MongoDB) serait idéale pour stocker des documents JSON représentant les leçons et les configurations de cube, ou simplement des fichiers statiques gérés par le service.
* **Justification pour le TP :** C'est le deuxième service idéal (objectif 14/20). Il est simple, principalement en lecture, et permet de démontrer la communication entre services (ex: l'`User Service` demande au `Learning Service` si un utilisateur a terminé une leçon spécifique).

**Service 3 : `Session & Matchmaking Service` (L'aspect "Chess.com" et temps réel) - *Optionnel pour le début du TP***

* **Responsabilités :**
* Gérer les sessions de résolution "solo" (chronomètre, validation du scramble, enregistrement du temps).
* Gérer les parties classées en duel (matchmaking basé sur le PB ou un système Elo).
* Communiquer les temps en temps réel (nécessitera probablement des WebSockets).


* **Base de données :** Redis (pour le matchmaking rapide et la gestion des sessions actives) et éventuellement PostgreSQL pour l'historique des matchs.
* **Justification pour le TP :** Ce service est plus complexe. Je te conseille de le garder pour la fin, ou de l'implémenter de manière très simplifiée (ex: juste enregistrer un temps sans matchmaking complexe) pour te concentrer sur les aspects Kubernetes (Gateway, Sécurité) qui rapportent plus de points dans ce TP spécifique.

#### 3. L'Infrastructure (Conforme au TP)

* **API Gateway (Ingress / Istio) :**
* C'est le point d'entrée unique pour ton application React.
* Elle route les requêtes `/api/users` vers le `User Service`, `/api/lessons` vers le `Learning Service`, etc.
* Obligatoire pour atteindre le palier 12/20.




* **Docker & Kubernetes :**
* Chaque service (Front-end, Service 1, Service 2, Service 3) aura son propre `Dockerfile`.
* Tu créeras des manifestes Kubernetes (`Deployment`, `Service`) pour chaque microservice.
* Tu utiliseras Minikube (comme suggéré dans l'énoncé) pour le développement local.





### Plan d'action recommandé pour le TP

Puisque le barème est très orienté "DevOps/Infra", voici comment je te conseille de procéder :

1. **Semaine 1 (Objectif 10/20) :**
* Crée un service très basique en Python (par exemple, le `User Service` avec juste une route `/users` qui renvoie un faux utilisateur en dur).
* Fais le `Dockerfile`, build l'image, pousse-la sur Docker Hub.
* Fais le fichier `deployment.yaml` et `service.yaml` pour Kubernetes. Déploie sur Minikube et vérifie que tu peux l'appeler.


2. **Semaine 2 (Objectif 12/20 & 14/20) :**
* Crée le deuxième service (`Learning Service` basique). Conteneurise-le et déploie-le.
* Mets en place un Ingress Controller (ou Istio) sur ton Minikube pour router le trafic (ex: `localhost/users` -> Service 1, `localhost/lessons` -> Service 2).


3. **Semaine 3 (Objectif 16/20) :**
* Ajoute une base de données MySQL ou PostgreSQL dans ton cluster Kubernetes (ou utilise une DBaaS si tu es à l'aise).
* Modifie le `User Service` pour qu'il lise/écrive dans cette base.


4. **Semaine 4 et suivantes (Objectif 18/20, 20/20 et Fonctionnalités métier) :**
* Implémente la sécurité (RBAC ou mTLS).


* *Maintenant que l'architecture est notée et validée*, tu peux te concentrer sur le front-end React, le cube 3D (Three.js), les binds clavier complexes, et la vraie logique de ton application (les temps, les algos, etc.).



L'idée de l'application est géniale, mais n'oublie pas que **pour ce TP, un code "simple" qui tourne parfaitement sur un cluster Kubernetes sécurisé et bien configuré rapportera plus de points qu'une application React 3D magnifique qui ne tourne qu'en local avec Docker Compose.**