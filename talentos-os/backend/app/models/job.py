import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, Boolean, DateTime, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class JobStatus(str, enum.Enum):
    ATIVA      = "ativa"
    PAUSADA    = "pausada"
    CRITICA    = "critica"
    ENCERRADA  = "encerrada"
    PREENCHIDA = "preenchida"

class JobUrgency(str, enum.Enum):
    BAIXA   = "baixa"
    MEDIA   = "media"
    ALTA    = "alta"
    CRITICA = "critica"

class Job(db.Model):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    area: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    level: Mapped[str | None] = mapped_column(String(60), nullable=True)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    modality: Mapped[str | None] = mapped_column(String(40), nullable=True)
    contract_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    salary_range_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_range_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    headcount_approved: Mapped[int] = mapped_column(Integer, default=1)
    candidates_target: Mapped[int] = mapped_column(Integer, default=15)
    status: Mapped[JobStatus] = mapped_column(SAEnum(JobStatus, name="job_status"), default=JobStatus.ATIVA, nullable=False, index=True)
    urgency: Mapped[JobUrgency] = mapped_column(SAEnum(JobUrgency, name="job_urgency"), default=JobUrgency.MEDIA, nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requires_language: Mapped[bool] = mapped_column(Boolean, default=False)
    required_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cell_id: Mapped[int | None] = mapped_column(db.ForeignKey("cells.id"), nullable=True)
    recruiter_id: Mapped[int | None] = mapped_column(db.ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    candidates = relationship("Candidate", back_populates="job", lazy="dynamic")
    interviews = relationship("Interview", back_populates="job")
    recruiter = relationship("User", foreign_keys=[recruiter_id])

    @property
    def candidates_count(self) -> int:
        return self.candidates.count()

    @property
    def fill_percentage(self) -> float:
        if self.candidates_target == 0: return 0.0
        return round(min(self.candidates_count / self.candidates_target * 100, 100), 1)

    def to_dict(self) -> dict:
        return {
            "id":self.id,"title":self.title,"area":self.area,"level":self.level,
            "location":self.location,"modality":self.modality,"contract_type":self.contract_type,
            "status":self.status.value,"urgency":self.urgency.value,
            "candidates_count":self.candidates_count,"candidates_target":self.candidates_target,
            "fill_percentage":self.fill_percentage,
            "deadline":self.deadline.isoformat() if self.deadline else None,
            "requires_language":self.requires_language,"required_language":self.required_language,
            "salary_range_min":self.salary_range_min,"salary_range_max":self.salary_range_max,
            "description":self.description,"requirements":self.requirements or [],
            "created_at":self.created_at.isoformat(),
        }
