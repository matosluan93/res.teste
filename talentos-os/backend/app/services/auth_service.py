from datetime import datetime, timezone
from flask_jwt_extended import create_access_token, create_refresh_token
from ..repositories.user_repo import UserRepository
from ..models.user import User

user_repo = UserRepository()

class AuthService:
    def login(self, email: str, password: str) -> dict:
        user = user_repo.get_by_email(email)
        if not user or not user.check_password(password):
            raise ValueError("Credenciais inválidas")
        if not user.is_active:
            raise ValueError("Usuário desativado")
        user.last_login = datetime.now(timezone.utc)
        user_repo.save()
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }

    def refresh_token(self, user_id: int) -> dict:
        user = user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("Usuário não encontrado")
        return {"access_token": create_access_token(identity=str(user.id))}

    def create_user(self, name: str, email: str, password: str, role: str = "recruiter") -> User:
        if user_repo.exists_by_email(email):
            raise ValueError("E-mail já cadastrado")
        user = user_repo.create(name=name, email=email, role=role)
        user.set_password(password)
        user_repo.save()
        return user

auth_service = AuthService()
