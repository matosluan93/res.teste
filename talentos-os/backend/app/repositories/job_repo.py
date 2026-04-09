from typing import List
from sqlalchemy import select, func
from ..extensions import db
from ..models.job import Job, JobStatus
from .base import BaseRepository

class JobRepository(BaseRepository[Job]):
    def __init__(self):
        super().__init__(Job)

    def get_active(self) -> List[Job]:
        return db.session.scalars(
            select(Job).where(Job.status.in_([JobStatus.ATIVA, JobStatus.CRITICA]))
            .order_by(Job.urgency.desc(), Job.created_at.desc())
        ).all()

    def get_by_area(self, area: str) -> List[Job]:
        return db.session.scalars(select(Job).where(Job.area == area)).all()

    def count_by_status(self) -> dict:
        result = db.session.execute(
            select(Job.status, func.count(Job.id)).group_by(Job.status)
        ).all()
        return {row[0].value: row[1] for row in result}
