import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.config import ProductionConfig


@pytest.mark.parametrize("secret,jwt_secret", [
    (None, None),
    ("x" * 32, "short-key"),
    ("x" * 32, "x" * 32),
])
def test_production_rejects_unsafe_keys(monkeypatch, secret, jwt_secret):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", secret)
    monkeypatch.setattr(ProductionConfig, "JWT_SECRET_KEY", jwt_secret)
    with pytest.raises(RuntimeError, match="SECRET_KEY e JWT_SECRET_KEY"):
        create_app("production")


def test_rejects_token_signed_with_old_default(client):
    issuer = create_app("testing")
    issuer.config["JWT_SECRET_KEY"] = "jwt-dev-key-change-in-prod"
    with issuer.app_context():
        token = create_access_token(identity="1")
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json["message"] == "Token inválido ou expirado"


def test_ai_error_omits_provider_details(client, auth_headers, monkeypatch):
    from app.routes.ai import ai_service

    def fail(*args, **kwargs):
        raise ValueError("private provider data")

    monkeypatch.setattr(ai_service, "analyze_cv", fail)
    response = client.post("/api/ai/analyze-cv", headers=auth_headers, json={"cv_text": "synthetic " * 8})
    assert response.status_code == 500
    assert response.json["error"] == "ai_error"
    assert "private provider data" not in response.get_data(as_text=True)
