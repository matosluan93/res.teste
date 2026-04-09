from typing import Optional
from sqlalchemy import select
from ..extensions import db
from ..models.user import User
from .base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, email: str) -> Optional[User]:
        return db.session.scalar(select(User).where(User.email == email))

    def get_active_users(self):
        return db.session.scalars(select(User).where(User.is_active == True)).all()

    def exists_by_email(self, email: str) -> bool:
        return db.session.scalar(select(User.id).where(User.email == email)) is not None
