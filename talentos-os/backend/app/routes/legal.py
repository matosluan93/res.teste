from flask import Blueprint, jsonify
from ..middleware.auth import login_required
from ..extensions import db
from ..models.assessment import LegalAnalysis

legal_bp = Blueprint("legal", __name__)

@legal_bp.get("/")
@login_required
def list_analyses():
    analyses = db.session.scalars(db.select(LegalAnalysis).order_by(LegalAnalysis.created_at.desc())).all()
    return jsonify([a.to_dict() for a in analyses]), 200

@legal_bp.get("/<int:id>")
@login_required
def get_analysis(id):
    analysis = db.session.get(LegalAnalysis, id)
    if not analysis:
        return jsonify({"error": "not_found"}), 404
    return jsonify(analysis.to_dict()), 200
