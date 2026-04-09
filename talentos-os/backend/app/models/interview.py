import enum
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class InterviewType(str, enum.Enum):
    RH            = "entrevista_rh"
    TECNICA       = "tecnica_presencial"
    TECNICA_VIDEO = "tecnica_video"
    BANCA         = "banca_executiva"
    CASE          = "case_desafio"
    PAINEL        = "painel_time"

class InterviewStatus(str, enum.Enum):
    AGENDADA   = "agendada"
    REALIZADA  = "realizada"
    CANCELADA  = "cancelada"
    REAGENDADA = "reagendada"
    REPROVADO  = "reprovado"
    APROVADO   = "aprovado"

class InviteType(str, enum.Enum):
    DIRETO    = "convite_direto"
    PERGUNTAS = "pre_perguntas"

class Interview(db.Model):
    __tablename__ = "interviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    interviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    type: Mapped[InterviewType] = mapped_column(SAEnum(InterviewType, name="interview_type"), nullable=False)
    status: Mapped[InterviewStatus] = mapped_column(SAEnum(InterviewStatus, name="interview_status"), default=InterviewStatus.AGENDADA, nullable=False, index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, default=60)
    meeting_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    candidate = relationship("Candidate", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    interviewer = relationship("User", back_populates="interviews_as_interviewer", foreign_keys=[interviewer_id])
    invite = relationship("InterviewInvite", back_populates="interview", uselist=False)

    def to_dict(self) -> dict:
        return {
            "id":self.id,"candidate_id":self.candidate_id,
            "candidate_name":self.candidate.name if self.candidate else None,
            "job_id":self.job_id,"job_title":self.job.title if self.job else None,
            "interviewer_name":self.interviewer.name if self.interviewer else None,
            "type":self.type.value,"status":self.status.value,
            "scheduled_at":self.scheduled_at.isoformat() if self.scheduled_at else None,
            "meeting_link":self.meeting_link,"feedback":self.feedback,
            "feedback_score":self.feedback_score,"created_at":self.created_at.isoformat(),
        }

class InterviewInvite(db.Model):
    __tablename__ = "interview_invites"
    id: Mapped[int] = mapped_column(primary_key=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"), nullable=False)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    recruiter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    invite_type: Mapped[InviteType] = mapped_column(SAEnum(InviteType, name="invite_type"), nullable=False)
    whatsapp_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    message_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    whatsapp_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="enviado")
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    interview = relationship("Interview", back_populates="invite")
    candidate = relationship("Candidate")
    recruiter = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id":self.id,"interview_id":self.interview_id,
            "candidate_name":self.candidate.name if self.candidate else None,
            "invite_type":self.invite_type.value,"status":self.status,
            "whatsapp_url":self.whatsapp_url,"sent_at":self.sent_at.isoformat(),
        }
