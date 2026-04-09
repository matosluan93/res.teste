from flask import Blueprint, request, jsonify
from ..middleware.auth import login_required, require_permission
from ..extensions import db
from ..models.audit import AuditLog

audit_bp = Blueprint("audit", __name__)

@audit_bp.get("/")
@login_required
@require_permission("auditoria")
def list_logs():
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 50)), 100)
    stmt = db.select(AuditLog).order_by(AuditLog.created_at.desc())
    result = db.paginate(stmt, page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": [log.to_dict() for log in result.items],
        "total": result.total,
        "page": result.page,
        "pages": result.pages,
    }), 200
