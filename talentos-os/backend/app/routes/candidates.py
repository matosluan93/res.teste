from flask import Blueprint, request, jsonify, g
from ..middleware.auth import login_required, require_permission
from ..services.candidate_service import candidate_service
from ..services.audit_service import audit_service

candidates_bp = Blueprint("candidates", __name__)

@candidates_bp.get("/")
@login_required
def list_candidates():
    filters = {k: request.args.get(k) for k in ("q","stage","area","source","score_min")}
    filters = {k: v for k, v in filters.items() if v}
    if "score_min" in filters:
        try: filters["score_min"] = float(filters["score_min"])
        except: del filters["score_min"]
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 100)
    result = candidate_service.list_candidates(filters, page, per_page)
    return jsonify({
        **result,
        "items": [c.to_dict() for c in result["items"]],
    }), 200

@candidates_bp.get("/<int:id>")
@login_required
def get_candidate(id):
    try:
        c = candidate_service.get_candidate(id)
        return jsonify(c.to_dict(detailed=True)), 200
    except ValueError as e:
        return jsonify({"error": "not_found", "message": str(e)}), 404

@candidates_bp.post("/")
@login_required
def create_candidate():
    data = request.get_json() or {}
    required = ["name", "email"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": "validation_error", "message": f"Campos obrigatórios: {missing}"}), 422
    try:
        c = candidate_service.create_candidate(data, g.current_user.id)
        audit_service.log(g.current_user.id, "candidate_created", "candidate", c.id, f"Candidato criado: {c.name}")
        return jsonify(c.to_dict()), 201
    except Exception as e:
        return jsonify({"error": "server_error", "message": str(e)}), 500

@candidates_bp.put("/<int:id>")
@login_required
def update_candidate(id):
    data = request.get_json() or {}
    try:
        c = candidate_service.update_candidate(id, data)
        audit_service.log(g.current_user.id, "candidate_updated", "candidate", c.id, f"Candidato atualizado: {c.name}")
        return jsonify(c.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": "not_found", "message": str(e)}), 404

@candidates_bp.patch("/<int:id>/stage")
@login_required
def advance_stage(id):
    data = request.get_json() or {}
    stage = data.get("stage")
    if not stage:
        return jsonify({"error": "validation_error", "message": "Campo stage é obrigatório"}), 422
    try:
        c = candidate_service.advance_stage(id, stage)
        audit_service.log(g.current_user.id, "stage_advanced", "candidate", c.id, f"{c.name} → {stage}")
        return jsonify(c.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": "not_found", "message": str(e)}), 404

@candidates_bp.delete("/<int:id>")
@login_required
@require_permission("configuracoes")
def delete_candidate(id):
    try:
        candidate_service.delete_candidate(id)
        audit_service.log(g.current_user.id, "candidate_deleted", "candidate", id)
        return jsonify({"message": "Candidato removido"}), 200
    except ValueError as e:
        return jsonify({"error": "not_found", "message": str(e)}), 404

@candidates_bp.get("/pipeline/board")
@login_required
def pipeline_board():
    return jsonify(candidate_service.get_pipeline_board()), 200
