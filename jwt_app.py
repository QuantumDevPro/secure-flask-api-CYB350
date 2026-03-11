from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your_secret_key"
jwt = JWTManager(app)

# بيانات المستخدمين
users = [
    {"id": 1, "username": "admin", "password": "1234"},
    {"id": 2, "username": "user", "password": "abcd"},
]

# ============================
# Public Endpoint 
# ============================
@app.get("/public")
def public():
    return jsonify(message="This is a public endpoint")


# ============================
# Login Endpoint
# ============================
@app.post("/login")
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = next((u for u in users if u["username"] == username and u["password"] == password), None)

    if not user:
        return jsonify(error="Invalid credentials"), 401

    token = create_access_token(identity=str(user["id"]))

    return jsonify(access_token=token)


# ============================
# Protected Endpoint
# ============================
@app.get("/protected")
@jwt_required()
def protected():
    user_id = int(get_jwt_identity())

    user = next((u for u in users if u["id"] == user_id), None)

    if not user:
        return jsonify(error="User not found"), 404

    return jsonify(message=f"Hello {user['username']}, you are authorized!")


# ============================
# Run Server
# ============================
if __name__ == "__main__":
    app.run(port=5000, debug=True)