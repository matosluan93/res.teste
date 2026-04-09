from flask import Blueprint, jsonify
from ..middleware.auth import login_required, require_permission
from ..extensions import db
from ..models.platform import Platform

platforms_bp = Blueprint("platforms", __name__)

@platforms_bp.get("/")
@login_required
@require_permission("plataformas")
def list_platforms():
    platforms = db.session.scalars(db.select(Platform)).all()
    return jsonify([p.to_dict() for p in platforms]), 200
