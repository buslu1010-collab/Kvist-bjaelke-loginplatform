import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.database import database, initialize_database
from app.schemas import UserCreate, UserLogin, UserResponse

from app.bcrypt_integration import hash_password, verify_password


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="SQLite User API",
    description="Et undervisnings-API til registrering og login.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3400", "http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


def integrity_error_to_http(error: sqlite3.IntegrityError) -> HTTPException:
    message = str(error).lower()
    if "username" in message:
        detail = "Brugernavnet er allerede i brug"
    elif "email" in message:
        detail = "E-mailadressen er allerede i brug"
    else:
        detail = "Dataene er i konflikt med en eksisterende bruger"
    return HTTPException(status_code=409, detail=detail)


@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(payload: UserCreate) -> dict[str, object]:
    try:
        with database() as connection:
            cursor = connection.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (
                    payload.username, 
                    str(payload.email), 
                       hash_password(payload.password) 
                ),
            )
            user = connection.execute(
                "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
    except sqlite3.IntegrityError as error:
        raise integrity_error_to_http(error) from error
    return dict(user)


@app.post("/login", response_model=UserResponse)
def login(payload: UserLogin) -> dict[str, object]:
    with database() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?", (payload.username,)
        ).fetchone()

   
    if user is None or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forkert brugernavn eller password",
        )

    return dict(user)
