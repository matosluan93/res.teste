from flask import Blueprint, request, jsonify, g
from ..middleware.auth import login_required
from ..repositories.job_repo import JobRepository
from ..services.audit_service import audit_service

jobs_bp = Blueprint("jobs", __name__)
job_repo = JobRepository()

@jobs_bp.get("/")
@login_required
def list_jobs():
    status = request.args.get("status")
    area = request.args.get("area")
    jobs = job_repo.get_active() if not status else job_repo.get_all()
    if area:
        jobs = [j for j in jobs if j.area == area]
    return jsonify([j.to_dict() for j in jobs]), 200

@jobs_bp.get("/<int:id>")
@login_required
def get_job(id):
    job = job_repo.get_by_id(id)
    if not job:
        return jsonify({"error": "not_found", "message": "Vaga não encontrada"}), 404
    return jsonify(job.to_dict()), 200

@jobs_bp.post("/")
@login_required
def create_job():
    data = request.get_json() or {}
    if not data.get("title") or not data.get("area"):
        return jsonify({"error": "validation_error", "message": "Título e área são obrigatórios"}), 422
    data["recruiter_id"] = g.current_user.id
    job = job_repo.create(**data)
    job_repo.save()
    audit_service.log(g.current_user.id, "job_created", "job", job.id, f"Vaga criada: {job.title}")
    return jsonify(job.to_dict()), 201

@jobs_bp.put("/<int:id>")
@login_required
def update_job(id):
    job = job_repo.get_by_id(id)
    if not job:
        return jsonify({"error": "not_found"}), 404
    data = request.get_json() or {}
    job_repo.update(job, **data)
    job_repo.save()
    return jsonify(job.to_dict()), 200

@jobs_bp.get("/stats/by-status")
@login_required
def stats_by_status():
    return jsonify(job_repo.count_by_status()), 200
