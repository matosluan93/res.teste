from flask import Flask, jsonify
from .config import config_by_name
from .extensions import db, migrate, jwt, cors, cache, limiter

def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "TalentOS API", "version": "4.0.0"}), 200

    return app

def _init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    cache.init_app(app)
    limiter.init_app(app)

def _register_blueprints(app):
    from .routes.auth import auth_bp
    from .routes.candidates import candidates_bp
    from .routes.jobs import jobs_bp
    from .routes.interviews import interviews_bp
    from .routes.legal import legal_bp
    from .routes.ai import ai_bp
    from .routes.analytics import analytics_bp
    from .routes.platforms import platforms_bp
    from .routes.cells import cells_bp
    from .routes.audit import audit_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(candidates_bp, url_prefix="/api/candidates")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(interviews_bp, url_prefix="/api/interviews")
    app.register_blueprint(legal_bp, url_prefix="/api/legal")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(platforms_bp, url_prefix="/api/platforms")
    app.register_blueprint(cells_bp, url_prefix="/api/cells")
    app.register_blueprint(audit_bp, url_prefix="/api/audit-logs")

def _register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e): return jsonify({"error":"bad_request","message":str(e)}),400
    @app.errorhandler(401)
    def unauthorized(e): return jsonify({"error":"unauthorized","message":"Token inválido ou expirado"}),401
    @app.errorhandler(403)
    def forbidden(e): return jsonify({"error":"forbidden","message":"Sem permissão para esta ação"}),403
    @app.errorhandler(404)
    def not_found(e): return jsonify({"error":"not_found","message":"Recurso não encontrado"}),404
    @app.errorhandler(422)
    def unprocessable(e): return jsonify({"error":"validation_error","message":str(e)}),422
    @app.errorhandler(429)
    def rate_limit(e): return jsonify({"error":"rate_limit","message":"Muitas requisições. Tente novamente."}),429
    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Internal error: {e}")
        return jsonify({"error":"server_error","message":"Erro interno do servidor"}),500
