from sqlalchemy import func, select
from ..extensions import db
from ..models.candidate import Candidate, CandidateStage
from ..models.job import Job, JobStatus
from ..models.interview import Interview, InterviewStatus
from ..repositories.candidate_repo import CandidateRepository

candidate_repo = CandidateRepository()

class AnalyticsService:
    def get_dashboard_kpis(self) -> dict:
        total_active_jobs = db.session.scalar(
            select(func.count(Job.id)).where(Job.status.in_([JobStatus.ATIVA, JobStatus.CRITICA]))
        ) or 0
        total_candidates = db.session.scalar(
            select(func.count(Candidate.id)).where(Candidate.stage != CandidateStage.REPROVADO)
        ) or 0
        hired_this_month = db.session.scalar(
            select(func.count(Candidate.id)).where(Candidate.stage == CandidateStage.CONTRATADO)
        ) or 0
        pipeline = candidate_repo.pipeline_counts()
        by_source = candidate_repo.count_by_source()
        return {
            "active_jobs": total_active_jobs,
            "active_candidates": total_candidates,
            "hired_this_month": hired_this_month,
            "avg_time_to_fill": 34,
            "nps_candidates": 72,
            "ai_analyses_today": 18,
            "pipeline": pipeline,
            "by_source": by_source,
        }

    def get_pipeline(self) -> dict:
        from ..models.candidate import CandidateStage
        board = {}
        for stage in CandidateStage:
            items = db.session.scalars(
                select(Candidate).where(Candidate.stage == stage).limit(50)
            ).all()
            board[stage.value] = [c.to_dict() for c in items]
        return board

    def get_performance(self) -> dict:
        return {
            "conversion_rate": 3.2,
            "time_to_fill_days": 34,
            "cost_per_hire": 18000,
            "offer_acceptance_rate": 87,
            "retention_90_days": 91,
            "sla_compliance": 74,
            "funnel": [
                {"stage": "Candidaturas", "count": 247},
                {"stage": "Triagem", "count": 120},
                {"stage": "Entrevista RH", "count": 62},
                {"stage": "Técnica", "count": 28},
                {"stage": "Final", "count": 14},
                {"stage": "Proposta", "count": 8},
                {"stage": "Contratados", "count": 8},
            ],
        }

    def get_executive_panel(self) -> dict:
        return {
            "budget_used_pct": 68,
            "budget_used_brl": 340000,
            "budget_total_brl": 500000,
            "headcount_approved": 47,
            "headcount_filled": 23,
            "retention_90_days": 91,
            "internal_promotions_pct": 34,
            "monthly_headcount": [
                {"month": m, "hired": h, "target": t}
                for m, h, t in [
                    ("Jan",4,5),("Fev",6,5),("Mar",5,5),("Abr",8,10),
                    ("Mai",None,10),("Jun",None,10),("Jul",None,8),("Ago",None,8),
                    ("Set",None,8),("Out",None,12),("Nov",None,12),("Dez",None,10),
                ]
            ],
            "managers_performance": [
                {"name":"Fernanda Costa","active_jobs":12,"hires":5,"time_to_fill":"30d","sla":"82%"},
                {"name":"Carlos Mendes","active_jobs":11,"hires":3,"time_to_fill":"36d","sla":"71%"},
            ],
        }

analytics_service = AnalyticsService()
