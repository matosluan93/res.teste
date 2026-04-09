from functools import wraps
from flask import jsonify, request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..repositories.user_repo import UserRepository

user_repo = UserRepository()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = user_repo.get_by_id(int(user_id))
            if not user or not user.is_active:
                return jsonify({"error": "unauthorized", "message": "Usuário inativo ou não encontrado"}), 401
            g.current_user = user
        except Exception as e:
            return jsonify({"error": "unauthorized", "message": str(e)}), 401
        return f(*args, **kwargs)
    return decorated

def require_permission(permission: str):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user:
                return jsonify({"error": "unauthorized"}), 401
            if not user.has_permission(permission):
                return jsonify({"error": "forbidden", "message": f"Permissão necessária: {permission}"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user or user.role.value not in roles:
                return jsonify({"error": "forbidden", "message": "Perfil de acesso insuficiente"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
