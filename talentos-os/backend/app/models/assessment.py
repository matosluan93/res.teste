import enum
from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, DateTime, Enum as SAEnum, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class LegalStatus(str, enum.Enum):
    APROVADO        = "aprovado"
    REPROVADO       = "reprovado"
    ANALISE_HUMANA  = "analise_humana"
    PENDENTE        = "pendente"

class LegalAnalysis(db.Model):
    __tablename__ = "legal_analyses"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, unique=True)
    analyst_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    natcorp_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    escavador_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    other_platforms_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LegalStatus] = mapped_column(SAEnum(LegalStatus, name="legal_status"), default=LegalStatus.PENDENTE, nullable=False, index=True)
    verdict: Mapped[str | None] = mapped_column(String(60), nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_report: Mapped[str | None] = mapped_column(Text, nullable=True)
    processes_count: Mapped[int] = mapped_column(Integer, default=0)
    has_criminal_record: Mapped[bool] = mapped_column(default=False)
    has_active_process: Mapped[bool] = mapped_column(default=False)
    requires_human_review: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    candidate = relationship("Candidate", back_populates="legal_analysis")
    analyst = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id":self.id,"candidate_id":self.candidate_id,"status":self.status.value,
            "verdict":self.verdict,"reasoning":self.reasoning,"full_report":self.full_report,
            "processes_count":self.processes_count,"has_criminal_record":self.has_criminal_record,
            "has_active_process":self.has_active_process,"requires_human_review":self.requires_human_review,
            "created_at":self.created_at.isoformat(),
        }

class LanguageAssessment(db.Model):
    __tablename__ = "language_assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    assessor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    cefr_level: Mapped[str | None] = mapped_column(String(5), nullable=True)
    descriptive_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    score_speaking: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_writing: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_listening: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_reading: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_vocabulary: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_grammar: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_fluency: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_overall: Mapped[float | None] = mapped_column(Float, nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    recording_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(40), nullable=True)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    candidate = relationship("Candidate", back_populates="language_assessments")
    assessor = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id":self.id,"candidate_id":self.candidate_id,"language":self.language,
            "cefr_level":self.cefr_level,"descriptive_level":self.descriptive_level,
            "score_overall":self.score_overall,"score_speaking":self.score_speaking,
            "score_writing":self.score_writing,"score_listening":self.score_listening,
            "score_reading":self.score_reading,"recommendation":self.recommendation,
            "justification":self.justification,"created_at":self.created_at.isoformat(),
        }

class CVAnalysis(db.Model):
    __tablename__ = "cv_analyses"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int | None] = mapped_column(ForeignKey("candidates.id"), nullable=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    analyst_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    cv_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    candidate_name_raw: Mapped[str | None] = mapped_column(String(120), nullable=True)
    score_overall: Mapped[float | None] = mapped_column(Float, nullable=True)
    fit_technical: Mapped[float | None] = mapped_column(Float, nullable=True)
    fit_cultural: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    candidate = relationship("Candidate", back_populates="cv_analyses")
    analyst = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id":self.id,"candidate_id":self.candidate_id,
            "candidate_name":self.candidate_name_raw,"score_overall":self.score_overall,
            "fit_technical":self.fit_technical,"fit_cultural":self.fit_cultural,
            "recommendation":self.recommendation,"ai_result":self.ai_result,
            "created_at":self.created_at.isoformat(),
        }
