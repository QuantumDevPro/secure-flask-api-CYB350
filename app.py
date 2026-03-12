from flask import Flask, jsonify, request
from flasgger import Swagger
from flask import redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from functools import wraps
from key_manager import get_api_key
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)  

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# ============================
# SECRET KEY
# Required for OAuth sessions
# ============================
app.secret_key = "lab12_secret_key"


# ---------------------------------------------------------------------------
# Swagger config
# ---------------------------------------------------------------------------
app.config["SWAGGER"] = {
    "title": "Items API",
    "specs": [{"endpoint": "swagger", "route": "/swagger.json"}],
    "specs_route": "/docs",
    "swagger_ui": True,
}
swagger = Swagger(app, template_file="swagger.yaml")


# ============================
# OAuth2 Configuration
# ============================

oauth = OAuth(app)

# GitHub OAuth configuration
oauth.register(
    name='github',
    client_id='Ov23liiGr6qDW3UjCmTv',
    client_secret='1556ead939c5257ecb7f475b6e21ef23bf839e39',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={
        'scope': 'user:email'
    }
)

# ============================
# Login Route
# ============================
@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

# ============================
# Callback Route
# ============================
@app.route("/authorize")
def authorize():
    token = oauth.github.authorize_access_token()
    session["user_token"] = token
    # Fetch user profile from GitHub
    resp = oauth.github.get("user")
    profile = resp.json()

    # Store user info in session
    session["user"] = profile["login"]
    session["user_token"] = token

    return jsonify({
        "message": "OAuth2 Authentication Successful",
        "github_user": profile["login"]
    })

# ---------------------------------------------------------------------------
# In-memory "database"
# ---------------------------------------------------------------------------
items = []
next_id = 1


def find_item(item_id):
    for index, item in enumerate(items):
        if item["id"] == item_id:
            return item, index
    return None, None


# -------------------------------
# # API KEY DECORATOR
# -------------------------------

EXCLUDED_ROUTES = [
    "/docs",
    "/swagger.json",
    "/login",
    "/authorize"
]

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if request.path in EXCLUDED_ROUTES:
            return f(*args, **kwargs)

        key = request.headers.get("X-API-Key")
        if not key or key != get_api_key():
            return jsonify({"error": "Unauthorized. invalid or missing API key"}), 401

        return f(*args, **kwargs)
    return decorated



# ---------------------------------------------------------------------------
# ROOT
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return jsonify({"message": "Secure API is running!", "status": "ok"})


# ---------------------------------------------------------------------------
# GET /items
# ---------------------------------------------------------------------------
@app.route("/items", methods=["GET"])
@require_api_key
@limiter.limit("5 per minute")
def get_items():
    return jsonify({
        "items": items,
        "total": len(items)
    }), 200


# ---------------------------------------------------------------------------
# GET /items/<id>
# ---------------------------------------------------------------------------
@app.route("/items/<int:item_id>", methods=["GET"])
@require_api_key
def get_item(item_id):
    item, _ = find_item(item_id)
    if item is None:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404
    return jsonify(item), 200


# ---------------------------------------------------------------------------
# POST /items
# ---------------------------------------------------------------------------
@app.route("/items", methods=["POST"])
@require_api_key
def create_item():
    global next_id

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    if "name" not in data:
        return jsonify({"error": "Missing required field: name"}), 400
    if "quantity" not in data:
        return jsonify({"error": "Missing required field: quantity"}), 400
    if not isinstance(data["quantity"], int) or data["quantity"] < 0:return jsonify({"error": "quantity must be a non-negative integer"}), 400

    new_item = {
        "id": next_id,
        "name": str(data["name"]).strip(),
        "quantity": data["quantity"]
    }

    items.append(new_item)
    next_id += 1

    return jsonify(new_item), 201


# ---------------------------------------------------------------------------
# PUT /items/<id>
# ---------------------------------------------------------------------------
@app.route("/items/<int:item_id>", methods=["PUT"])
@require_api_key
def update_item(item_id):

    item, index = find_item(item_id)
    if item is None:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "name" in data:
        item["name"] = str(data["name"]).strip()

    if "quantity" in data:
        if not isinstance(data["quantity"], int) or data["quantity"] < 0:
            return jsonify({"error": "quantity must be a non-negative integer"}), 400
        item["quantity"] = data["quantity"]

    items[index] = item
    return jsonify(item), 200


# ---------------------------------------------------------------------------
# DELETE /items/<id>
# ---------------------------------------------------------------------------
@app.route("/items/<int:item_id>", methods=["DELETE"])
@require_api_key
def delete_item(item_id):

    item, index = find_item(item_id)
    if item is None:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404

    items.pop(index)
    return jsonify({"message": f"Item {item_id} deleted successfully"}), 200

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": str(e.description)
    }), 429
    
# ---------------------------------------------------------------------------
# RUN APP
# ---------------------------------------------------------------------------
if __name__ == "__main__":
        app.run(
        debug=True,
        ssl_context=("cert/cert.pem", "cert/key.pem")
    )