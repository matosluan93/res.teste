import enum
from datetime import datetime, timezone
import bcrypt
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class UserRole(str, enum.Enum):
    RECRUITER = "recruiter"
    MANAGER   = "manager"
    EXECUTIVE = "executive"

ROLE_PERMISSIONS = {
    UserRole.RECRUITER: {
        "dashboard","curriculos","talentos","vagas","pipeline",
        "entrevistas","convites","comparativo","cv_analysis",
        "idiomas","perfis","executivos","juridico",
    },
    UserRole.MANAGER: {
        "dashboard","curriculos","talentos","vagas","pipeline",
        "entrevistas","convites","comparativo","cv_analysis",
        "idiomas","perfis","executivos","juridico",
        "plataformas","celulas","performance","relatorios","auditoria","configuracoes",
    },
    UserRole.EXECUTIVE: {
        "dashboard","curriculos","talentos","vagas","pipeline",
        "entrevistas","convites","comparativo","cv_analysis",
        "idiomas","perfis","executivos","juridico",
        "plataformas","celulas","performance","relatorios","auditoria","configuracoes",
        "exec_panel","aprovacoes","gestores",
    },
}

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"), nullable=False, default=UserRole.RECRUITER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cell_id: Mapped[int | None] = mapped_column(db.ForeignKey("cells.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    audit_logs = relationship("AuditLog", back_populates="user", lazy="dynamic")
    interviews_as_interviewer = relationship("Interview", back_populates="interviewer", foreign_keys="Interview.interviewer_id")

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def has_permission(self, perm: str) -> bool:
        return perm in ROLE_PERMISSIONS.get(self.role, set())

    @property
    def permissions(self) -> set:
        return ROLE_PERMISSIONS.get(self.role, set())

    def _get_initials(self) -> str:
        parts = self.name.split()
        return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else self.name[:2].upper()

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "email": self.email,
            "role": self.role.value, "is_active": self.is_active,
            "initials": self._get_initials(),
            "permissions": list(self.permissions),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
        }
