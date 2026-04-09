from flask import Blueprint, jsonify
from ..middleware.auth import login_required, require_permission
from ..services.analytics_service import analytics_service

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.get("/dashboard")
@login_required
def dashboard():
    return jsonify(analytics_service.get_dashboard_kpis()), 200

@analytics_bp.get("/pipeline")
@login_required
def pipeline():
    return jsonify(analytics_service.get_pipeline()), 200

@analytics_bp.get("/performance")
@login_required
@require_permission("performance")
def performance():
    return jsonify(analytics_service.get_performance()), 200

@analytics_bp.get("/executive")
@login_required
@require_permission("exec_panel")
def executive():
    return jsonify(analytics_service.get_executive_panel()), 200
