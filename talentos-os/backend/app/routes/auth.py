from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.auth_service import auth_service
from ..middleware.auth import login_required
from ..extensions import limiter

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "validation_error", "message": "E-mail e senha são obrigatórios"}), 422
    try:
        result = auth_service.login(email, password)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "unauthorized", "message": str(e)}), 401

@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = int(get_jwt_identity())
    try:
        result = auth_service.refresh_token(user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": "unauthorized", "message": str(e)}), 401

@auth_bp.post("/logout")
@login_required
def logout():
    return jsonify({"message": "Logout realizado com sucesso"}), 200

@auth_bp.get("/me")
@login_required
def me():
    return jsonify(g.current_user.to_dict()), 200
