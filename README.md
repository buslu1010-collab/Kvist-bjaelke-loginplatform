.# To run the Python API

## Kør hele løsningen med Keycloak

Kopiér `.env.example` til `.env`, vælg et admin-password, og start derefter
frontend, API og Keycloak:

```bash
docker compose up --build
```

Frontend kan nu åbnes på <http://localhost:3400>. Her kan man enten bruge det
almindelige login/oprette en lokal bruger eller vælge **Log ind med Keycloak**.
Det importerede undervisnings-realm indeholder denne testbruger:

- Brugernavn: `keycloak-demo`
- Password: `demo1234`

Keycloaks admin-konsol findes på <http://localhost:8100/admin> og bruger
oplysningerne `KEYCLOAK_ADMIN_USERNAME` og `KEYCLOAK_ADMIN_PASSWORD` fra `.env`.

Keycloak-indstillingerne til frontend kan ændres med `VITE_KEYCLOAK_URL`,
`VITE_KEYCLOAK_REALM` og `VITE_KEYCLOAK_CLIENT_ID`. Ved andre frontend-adresser
skal klientens redirect URI og web origin også opdateres i realm-konfigurationen.

Et lille REST API bygget med FastAPI og SQLite. API'et kan oprette, hente,
opdatere og slette brugere.

> **Advarsel:** Denne undervisningsversion gemmer med vilje passwords i
> klartekst i kolonnen `password`. Det må ikke bruges i produktion eller med
> rigtige passwords.

## Kom i gang

Kræver Python 3.9 eller nyere.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

API'et kører nu på <http://127.0.0.1:8000>. Den interaktive Swagger-side findes
på <http://127.0.0.1:8000/docs>.

SQLite-filen oprettes automatisk som `data/app.db`. En anden placering kan
vælges med miljøvariablen `DATABASE_PATH`.

## Password og bcrypt

API'et gemmer værdien fra requestens `password` direkte i SQLite-kolonnen
`password`. Den separate fil `app/bcrypt_integration.py` indeholder funktionerne
`hash_password()` og `verify_password()` til en senere bcrypt-integration. Filen
er med vilje tilføjet til `.gitignore` og bliver derfor ikke versionsstyret.

## Endpoints

| Metode | Sti | Beskrivelse |
|---|---|---|
| `GET` | `/health` | Sundhedstjek |
| `POST` | `/users` | Opret bruger |
| `GET` | `/users` | Hent alle brugere |
| `GET` | `/users/{id}` | Hent én bruger |
| `PATCH` | `/users/{id}` | Opdater bruger |
| `DELETE` | `/users/{id}` | Slet bruger |
| `POST` | `/users/{id}/verify-password` | Kontrollér password |

Eksempel på oprettelse:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' \
  -d '{"username":"ada","email":"ada@example.com","password":"meget-hemmeligt"}'
```

## Tests

```bash
python -m pip install -r requirements-dev.txt
pytest
```
