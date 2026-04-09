from flask import request
from ..extensions import db
from ..models.audit import AuditLog

class AuditService:
    def log(self, user_id: int | None, action: str, resource: str | None = None,
            resource_id: int | None = None, detail: str | None = None, meta: dict | None = None) -> None:
        try:
            log = AuditLog(
                user_id=user_id, action=action, resource=resource,
                resource_id=resource_id, detail=detail, meta=meta,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get("User-Agent", "")[:255] if request else None,
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            pass  # Auditoria nunca deve quebrar a operação principal

audit_service = AuditService()
