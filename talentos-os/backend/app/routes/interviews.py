from flask import Blueprint, request, jsonify, g
from ..middleware.auth import login_required
from ..extensions import db
from ..models.interview import Interview, InterviewInvite, InterviewType, InterviewStatus, InviteType
from ..services.ai_service import ai_service
from ..services.audit_service import audit_service

interviews_bp = Blueprint("interviews", __name__)

@interviews_bp.get("/")
@login_required
def list_interviews():
    day_filter = request.args.get("day")
    stmt = db.select(Interview).order_by(Interview.scheduled_at.desc())
    interviews = db.session.scalars(stmt).all()
    return jsonify([i.to_dict() for i in interviews]), 200

@interviews_bp.get("/<int:id>")
@login_required
def get_interview(id):
    interview = db.session.get(Interview, id)
    if not interview:
        return jsonify({"error": "not_found"}), 404
    return jsonify(interview.to_dict()), 200

@interviews_bp.post("/")
@login_required
def create_interview():
    data = request.get_json() or {}
    if not data.get("candidate_id") or not data.get("type"):
        return jsonify({"error": "validation_error", "message": "candidate_id e type são obrigatórios"}), 422
    interview = Interview(
        candidate_id=data["candidate_id"],
        job_id=data.get("job_id"),
        interviewer_id=data.get("interviewer_id", g.current_user.id),
        type=data["type"],
        meeting_link=data.get("meeting_link"),
        notes=data.get("notes"),
    )
    if data.get("scheduled_at"):
        from dateutil.parser import parse
        interview.scheduled_at = parse(data["scheduled_at"])
    db.session.add(interview)
    db.session.commit()
    audit_service.log(g.current_user.id, "interview_scheduled", "interview", interview.id)
    return jsonify(interview.to_dict()), 201

@interviews_bp.patch("/<int:id>/feedback")
@login_required
def add_feedback(id):
    interview = db.session.get(Interview, id)
    if not interview:
        return jsonify({"error": "not_found"}), 404
    data = request.get_json() or {}
    interview.feedback = data.get("feedback")
    interview.feedback_score = data.get("feedback_score")
    interview.status = data.get("status", InterviewStatus.REALIZADA.value)
    db.session.commit()
    return jsonify(interview.to_dict()), 200

@interviews_bp.post("/invite")
@login_required
def send_invite():
    data = request.get_json() or {}
    required = ["candidate_id","recruiter_name","job_title","candidate_name","phone","invite_type"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": "validation_error", "message": f"Campos: {missing}"}), 422
    result = ai_service.generate_whatsapp_message(
        recruiter_name=data["recruiter_name"],
        job_title=data["job_title"],
        candidate_name=data["candidate_name"],
        phone=data["phone"],
        invite_type=data["invite_type"],
    )
    audit_service.log(g.current_user.id, "invite_sent", "candidate", data["candidate_id"],
        f"Convite {data['invite_type']} enviado para {data['candidate_name']}")
    return jsonify(result), 200
