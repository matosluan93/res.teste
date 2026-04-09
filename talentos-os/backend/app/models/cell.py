from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class Cell(db.Model):
    __tablename__ = "cells"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(10), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    members = relationship("CellMember", back_populates="cell", cascade="all, delete-orphan")

    @property
    def total_hired(self) -> int:
        return sum(m.hires_count for m in self.members)

    def to_dict(self) -> dict:
        return {
            "id":self.id,"name":self.name,"icon":self.icon,"color":self.color,
            "members_count":len(self.members),"total_hired":self.total_hired,
            "members":[m.to_dict() for m in self.members],
        }

class CellMember(db.Model):
    __tablename__ = "cell_members"
    id: Mapped[int] = mapped_column(primary_key=True)
    cell_id: Mapped[int] = mapped_column(ForeignKey("cells.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    active_jobs_count: Mapped[int] = mapped_column(Integer, default=0)
    hires_count: Mapped[int] = mapped_column(Integer, default=0)
    sla_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    cell = relationship("Cell", back_populates="members")
    user = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id":self.id,"user_id":self.user_id,
            "user_name":self.user.name if self.user else None,
            "active_jobs_count":self.active_jobs_count,
            "hires_count":self.hires_count,"sla_percentage":self.sla_percentage,
        }
