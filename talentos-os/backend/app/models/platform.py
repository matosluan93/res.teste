from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db

class Platform(db.Model):
    __tablename__ = "platforms"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    color: Mapped[str | None] = mapped_column(String(10), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(10), nullable=True)
    total_candidates: Mapped[int] = mapped_column(Integer, default=0)
    total_hired: Mapped[int] = mapped_column(Integer, default=0)
    avg_cost_per_hire: Mapped[float | None] = mapped_column(Float, nullable=True)
    conversion_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    active_jobs: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id":self.id,"name":self.name,"slug":self.slug,"is_active":self.is_active,
            "color":self.color,"icon":self.icon,"total_candidates":self.total_candidates,
            "total_hired":self.total_hired,"avg_cost_per_hire":self.avg_cost_per_hire,
            "conversion_rate":self.conversion_rate,"active_jobs":self.active_jobs,
        }
