# SaltPepper.py - Opgraderet til bcrypt!
from dotenv import load_dotenv
import os
import hmac
import hashlib
import bcrypt  # <-- Nyt bibliotek

load_dotenv()

PEPPER = os.getenv("PASSWORD_PEPPER")
if not PEPPER:
    raise ValueError("PASSWORD_PEPPER mangler i .env-filen!")


def hash_password(password: str) -> str:
    """
    Hasher et password med bcrypt og en global pepper.
    Returnerer en string klar til at gemme i databasen.
    """
    # 1. Kombiner password og pepper sikkert med HMAC
    peppered_password = hmac.new(
        key=PEPPER.encode('utf-8'),
        msg=password.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()  # Dette er altid en 64 tegn lang string

    # 2. Hash den pepperede værdi med bcrypt
    # bcrypt.gensalt() genererer og gemmer et unikt salt automatisk
    hashed = bcrypt.hashpw(
        password=peppered_password.encode('utf-8'),
        salt=bcrypt.gensalt(rounds=12)  # rounds=12 er anbefalet i 2026[reference:16][reference:17]
    )

    # bcrypt returnerer en bytes-string, vi konverterer til almindelig string for nem opbevaring
    return hashed.decode('utf-8')


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verificerer et password mod et gemt bcrypt-hash.
    """
    # 1. Kombiner password og pepper på præcis samme måde som ved hashing
    peppered_password = hmac.new(
        key=PEPPER.encode('utf-8'),
        msg=password.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    # 2. Sammenlign med det gemte hash ved hjælp af bcrypt's indbyggede funktion
    # bcrypt.checkpw håndterer at udtrække saltet fra stored_hash
    return bcrypt.checkpw(
        password=peppered_password.encode('utf-8'),
        hashed_password=stored_hash.encode('utf-8')
    )


# --- Eksempel på brug (test) ---
if __name__ == "__main__":
    print("🧪 Test af bcrypt + pepper:")
    test_pw = "hemmeligt_kodeord"

    # Hash passwordet
    hash_val = hash_password(test_pw)
    print(f"Hash (gem i DB): {hash_val}")

    # Verificer med det korrekte password
    ok = verify_password(test_pw, hash_val)
    print(f"Verificering OK: {ok}")

    # Verificer med et forkert password
    ok_forkert = verify_password("forkert_kode", hash_val)
    print(f"Forkert password: {ok_forkert}")