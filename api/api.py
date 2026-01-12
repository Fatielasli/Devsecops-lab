from flask import Flask, request, jsonify
import sqlite3
import subprocess
import hashlib
import os
import shlex

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-12345")  # Utiliser variable d'environnement

DATABASE = "users.db"

# --- Helpers ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password_md5(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

# --- Routes ---
@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")

    # Requête sécurisée avec paramètres
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"status": "success", "user": username})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host", "")
    if not host:
        return jsonify({"error": "No host provided"}), 400

    # Échapper l'input pour éviter l'injection shell
    safe_host = shlex.quote(host)
    try:
        output = subprocess.check_output(f"ping -c 1 {safe_host}", shell=True, text=True)
        return jsonify({"output": output})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/compute", methods=["POST"])
def compute():
    expression = request.json.get("expression", "")
    if not expression:
        return jsonify({"result": None})

    # Ne jamais utiliser eval sur input utilisateur
    try:
        # Limité aux calculs simples
        allowed_chars = "0123456789+-*/(). "
        if any(c not in allowed_chars for c in expression):
            return jsonify({"error": "Invalid characters in expression"}), 400
        result = eval(expression)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password", "")
    if not pwd:
        return jsonify({"error": "Password required"}), 400
    hashed = hash_password_md5(pwd)
    return jsonify({"md5": hashed})

@app.route("/readfile", methods=["POST"])
def readfile():
    filename = request.json.get("filename", "")
    if not filename:
        return jsonify({"error": "Filename required"}), 400

    # Protection contre path traversal
    if ".." in filename or filename.startswith("/"):
        return jsonify({"error": "Invalid filename"}), 400

    try:
        with open(filename, "r") as f:
            content = f.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug", methods=["GET"])
def debug():
    # Supprimer l’exposition de secrets
    return jsonify({"debug": True, "message": "Debug info hidden for security"})

@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Welcome to the DevSecOps API"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
