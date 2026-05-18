from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import os
import sqlite3
from pathlib import Path
from secrets import token_urlsafe
from uuid import uuid4

from ..models import AuthUserResponse


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
AUTH_DB_PATH = DATA_DIR / "auth.db"
SESSION_COOKIE_NAME = "chess_study_session"
SESSION_LIFETIME_DAYS = 30


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str
    display_name: str


def register_user(email: str, password: str, display_name: str) -> tuple[AuthUserResponse, str]:
    # Normalize user input early so the rest of the flow works with one
    # canonical representation.
    normalized_email = _normalize_email(email)
    clean_name = display_name.strip()
    if len(clean_name) < 2:
        raise ValueError("Display name must be at least 2 characters.")

    # SQLite is enough here because the project needs a lightweight local auth
    # store, not a separate database server.
    with _connect() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()
        if existing is not None:
            raise ValueError("An account already exists for this email.")

        user_id = str(uuid4())
        salt = os.urandom(16)
        password_hash = _hash_password(password, salt)
        now = _now_iso()
        connection.execute(
            """
            INSERT INTO users (id, email, display_name, password_hash, password_salt, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, normalized_email, clean_name, password_hash, _encode_bytes(salt), now),
        )
        session_token = _create_session(connection, user_id)
        connection.commit()

    return AuthUserResponse(id=user_id, email=normalized_email, display_name=clean_name), session_token


def login_user(email: str, password: str) -> tuple[AuthUserResponse, str]:
    normalized_email = _normalize_email(email)
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id, email, display_name, password_hash, password_salt
            FROM users
            WHERE email = ?
            """,
            (normalized_email,),
        ).fetchone()
        if row is None:
            raise ValueError("Invalid email or password.")

        expected_hash = row["password_hash"]
        salt = _decode_bytes(row["password_salt"])
        provided_hash = _hash_password(password, salt)
        # compare_digest is preferred for secrets because it avoids naive string
        # comparison patterns.
        if not hmac.compare_digest(provided_hash, expected_hash):
            raise ValueError("Invalid email or password.")

        session_token = _create_session(connection, row["id"])
        connection.commit()

    return (
        AuthUserResponse(id=row["id"], email=row["email"], display_name=row["display_name"]),
        session_token,
    )


def get_user_for_session(session_token: str | None) -> AuthUserResponse | None:
    if not session_token:
        return None

    with _connect() as connection:
        row = connection.execute(
            """
            SELECT users.id, users.email, users.display_name, sessions.expires_at
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (session_token,),
        ).fetchone()
        if row is None:
            return None

        expires_at = datetime.fromisoformat(row["expires_at"])
        if expires_at <= datetime.now(UTC):
            connection.execute("DELETE FROM sessions WHERE token = ?", (session_token,))
            connection.commit()
            return None

        return AuthUserResponse(id=row["id"], email=row["email"], display_name=row["display_name"])


def clear_session(session_token: str | None) -> None:
    if not session_token:
        return
    with _connect() as connection:
        connection.execute("DELETE FROM sessions WHERE token = ?", (session_token,))
        connection.commit()


def owner_key_for_user(user: AuthUserResponse | None) -> str:
    return "guest" if user is None else user.id


def _create_session(connection: sqlite3.Connection, user_id: str) -> str:
    token = token_urlsafe(32)
    connection.execute(
        """
        INSERT INTO sessions (token, user_id, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (token, user_id, _now_iso(), _expires_at_iso()),
    )
    return token


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(AUTH_DB_PATH)
    connection.row_factory = sqlite3.Row
    _ensure_schema(connection)
    return connection


def _ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if "@" not in normalized or "." not in normalized.split("@")[-1]:
        raise ValueError("Please enter a valid email address.")
    return normalized


def _hash_password(password: str, salt: bytes) -> str:
    # Never store raw passwords. PBKDF2 is a standard password hashing approach
    # for simple applications.
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 150_000)
    return _encode_bytes(derived)


def _encode_bytes(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _decode_bytes(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _expires_at_iso() -> str:
    return (datetime.now(UTC) + timedelta(days=SESSION_LIFETIME_DAYS)).isoformat()
