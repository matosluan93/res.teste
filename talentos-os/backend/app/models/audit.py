from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource: Mapped[str | None] = mapped_column(String(80), nullable=True)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    user = relationship("User", back_populates="audit_logs")

    def to_dict(self) -> dict:
        return {
            "id":self.id,"user_id":self.user_id,
            "user_name":self.user.name if self.user else "Sistema",
            "action":self.action,"resource":self.resource,"resource_id":self.resource_id,
            "detail":self.detail,"ip_address":self.ip_address,
            "created_at":self.created_at.isoformat(),
        }
