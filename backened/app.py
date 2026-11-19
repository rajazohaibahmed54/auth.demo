import secrets
import sqlite3
from functools import wraps
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)

DB_PATH = Path(__file__).resolve().parent / "auth.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )

        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", ("student",)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("student", generate_password_hash("pass123")),
            )


def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        with get_db() as conn:
            row = conn.execute(
                "SELECT id FROM tokens WHERE token = ?", (token,)
            ).fetchone()

        if not row:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)

    return decorated


def validate_login_input(data):
    if not isinstance(data, dict):
        return "Request body must be JSON"

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not username.strip():
        return "Username is required"

    if not isinstance(password, str) or not password:
        return "Password is required"

    username = username.strip()
    if len(username) < 3 or len(username) > 30:
        return "Username must be between 3 and 30 characters"

    if len(password) < 4:
        return "Password must be at least 4 characters"

    return None


@app.post("/login")
def login():
    data = request.get_json(silent=True)
    validation_error = validate_login_input(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    username = data["username"].strip()
    password = data["password"]

    with get_db() as conn:
        user = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            token = secrets.token_hex(16)
            conn.execute(
                "INSERT INTO tokens (token, user_id) VALUES (?, ?)",
                (token, user["id"]),
            )
            return jsonify({"token": token, "user": user["username"]})

    return jsonify({"error": "Invalid username or password"}), 401


@app.get("/secret-note")
@require_token
def secret_note():
    return jsonify({
        "note": "Authentication worked! Now backed by SQLite."
    })


init_db()

if __name__ == "__main__":
    app.run(port=5001, debug=True)