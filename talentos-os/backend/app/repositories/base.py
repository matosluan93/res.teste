from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Query
from ..extensions import db

T = TypeVar("T", bound=db.Model)

class BaseRepository(Generic[T]):
    """Repositório base com operações CRUD genéricas."""

    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        return db.session.get(self.model, id)

    def get_all(self) -> List[T]:
        return db.session.scalars(db.select(self.model)).all()

    def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.flush()
        return instance

    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.flush()
        return instance

    def delete(self, instance: T) -> None:
        db.session.delete(instance)
        db.session.flush()

    def save(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()

    def paginate(self, query: Query, page: int = 1, per_page: int = 20) -> dict:
        result = db.paginate(query, page=page, per_page=per_page, error_out=False)
        return {
            "items": result.items,
            "total": result.total,
            "page": result.page,
            "per_page": result.per_page,
            "pages": result.pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev,
        }
