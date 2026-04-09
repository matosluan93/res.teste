from typing import Optional, List
from sqlalchemy import select, func, and_, or_
from ..extensions import db
from ..models.candidate import Candidate, CandidateStage
from .base import BaseRepository

class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self):
        super().__init__(Candidate)

    def get_by_stage(self, stage: CandidateStage) -> List[Candidate]:
        return db.session.scalars(select(Candidate).where(Candidate.stage == stage)).all()

    def get_by_job(self, job_id: int) -> List[Candidate]:
        return db.session.scalars(select(Candidate).where(Candidate.job_id == job_id)).all()

    def get_talent_bank(self) -> List[Candidate]:
        return db.session.scalars(select(Candidate).where(Candidate.is_talent_bank == True)).all()

    def search(self, query: str = None, stage: str = None, area: str = None,
               source: str = None, score_min: float = None, page: int = 1, per_page: int = 20) -> dict:
        stmt = select(Candidate)
        conditions = []
        if query:
            conditions.append(or_(
                Candidate.name.ilike(f"%{query}%"),
                Candidate.current_role.ilike(f"%{query}%"),
                Candidate.email.ilike(f"%{query}%"),
            ))
        if stage:
            conditions.append(Candidate.stage == stage)
        if area:
            conditions.append(Candidate.area == area)
        if source:
            conditions.append(Candidate.source == source)
        if score_min is not None:
            conditions.append(Candidate.ai_score >= score_min)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Candidate.created_at.desc())
        return self.paginate(stmt, page, per_page)

    def pipeline_counts(self) -> dict:
        result = db.session.execute(
            select(Candidate.stage, func.count(Candidate.id))
            .group_by(Candidate.stage)
        ).all()
        return {row[0].value: row[1] for row in result}

    def count_by_source(self) -> list:
        result = db.session.execute(
            select(Candidate.source, func.count(Candidate.id))
            .where(Candidate.source.is_not(None))
            .group_by(Candidate.source)
        ).all()
        return [{"source": row[0].value if row[0] else "Outros", "count": row[1]} for row in result]
