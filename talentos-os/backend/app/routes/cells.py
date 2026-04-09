from flask import Blueprint, jsonify
from ..middleware.auth import login_required, require_permission
from ..extensions import db
from ..models.cell import Cell

cells_bp = Blueprint("cells", __name__)

@cells_bp.get("/")
@login_required
@require_permission("celulas")
def list_cells():
    cells = db.session.scalars(db.select(Cell).where(Cell.is_active == True)).all()
    return jsonify([c.to_dict() for c in cells]), 200
