import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, Boolean, DateTime, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class CandidateStage(str, enum.Enum):
    TRIAGEM       = "triagem"
    ENTREVISTA_RH = "entrevista_rh"
    TECNICA       = "tecnica"
    FINAL         = "final"
    PROPOSTA      = "proposta"
    CONTRATADO    = "contratado"
    REPROVADO     = "reprovado"
    BANCO         = "banco_talentos"

class PlatformSource(str, enum.Enum):
    LINKEDIN   = "LinkedIn"
    GUPY       = "Gupy"
    PANDAPE    = "Pandapé"
    INDICACAO  = "Indique & Ganhe"
    SITE       = "Site"
    HEADHUNTER = "Headhunter"
    BANCO      = "Banco de Talentos"

class Candidate(db.Model):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    area: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    education: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skills: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    stage: Mapped[CandidateStage] = mapped_column(SAEnum(CandidateStage, name="candidate_stage"), default=CandidateStage.TRIAGEM, nullable=False, index=True)
    source: Mapped[PlatformSource | None] = mapped_column(SAEnum(PlatformSource, name="platform_source"), nullable=True)
    job_id: Mapped[int | None] = mapped_column(db.ForeignKey("jobs.id"), nullable=True, index=True)
    recruiter_id: Mapped[int | None] = mapped_column(db.ForeignKey("users.id"), nullable=True)
    ai_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_fit_technical: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_fit_cultural: Mapped[float | None] = mapped_column(Float, nullable=True)
    main_language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    disc_profile: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recruiter_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_talent_bank: Mapped[bool] = mapped_column(Boolean, default=False)
    salary_expectation: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    job = relationship("Job", back_populates="candidates")
    recruiter = relationship("User", foreign_keys=[recruiter_id])
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    legal_analysis = relationship("LegalAnalysis", back_populates="candidate", uselist=False)
    language_assessments = relationship("LanguageAssessment", back_populates="candidate")
    cv_analyses = relationship("CVAnalysis", back_populates="candidate")

    def to_dict(self, detailed: bool = False) -> dict:
        d = {
            "id":self.id,"name":self.name,"email":self.email,"phone":self.phone,
            "city":self.city,"current_role":self.current_role,"area":self.area,
            "stage":self.stage.value,"source":self.source.value if self.source else None,
            "ai_score":self.ai_score,"main_language":self.main_language,
            "language_level":self.language_level,"is_talent_bank":self.is_talent_bank,
            "created_at":self.created_at.isoformat(),
        }
        if detailed:
            d.update({
                "cpf":self.cpf,"linkedin_url":self.linkedin_url,"education":self.education,
                "experience_years":self.experience_years,"skills":self.skills or [],
                "ai_fit_technical":self.ai_fit_technical,"ai_fit_cultural":self.ai_fit_cultural,
                "language_score":self.language_score,"disc_profile":self.disc_profile,
                "recruiter_notes":self.recruiter_notes,"salary_expectation":self.salary_expectation,
                "job_id":self.job_id,"recruiter_id":self.recruiter_id,
            })
        return d
