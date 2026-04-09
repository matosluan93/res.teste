# TalentOS · Plataforma de R&S — Stefanini Brasil

Sistema interno full-stack de Recrutamento & Seleção com IA integrada.

## Stack

| Camada | Tech |
|---|---|
| Backend | Python 3.11 + Flask 3.0 |
| ORM | SQLAlchemy 2.0 + Alembic |
| Banco | PostgreSQL 16 |
| Cache | Redis 7 |
| Frontend | HTML5 + Vanilla JS (SPA) |
| Proxy | Nginx 1.25 |
| Container | Docker + Compose |
| IA | Claude (Anthropic API) |

## Início rápido

```bash
# 1. Clone e configure
git clone https://github.com/stefanini/talentos-os.git && cd talentos-os
cp .env.example .env
# Edite .env com ANTHROPIC_API_KEY e credenciais do banco

# 2. Suba os serviços
docker compose up --build

# 3. Migrations + seeds
docker compose exec backend flask db upgrade
docker compose exec backend flask seed

# 4. Acesse
# App:  http://localhost
# API:  http://localhost/api/health
```

## Logins de demo

| E-mail | Senha | Perfil |
|---|---|---|
| ana.lima@stefanini.com | Admin@2025 | Gerente Executiva R&S |
| fernanda.costa@stefanini.com | Manager@2025 | Gerente de RH |
| carlos.mendes@stefanini.com | Recruiter@2025 | Recrutador |
| demo@talentos.com | demo123 | Gerente Executiva R&S |

## Permissões (RBAC)

| Módulo | Recrutador | Gerente RH | Ger. Executiva |
|---|---|---|---|
| Dashboard, CVs, Pipeline, Entrevistas, IA | ✅ | ✅ | ✅ |
| Plataformas, Células, Performance, Relatórios | ❌ | ✅ | ✅ |
| Painel Executivo, Aprovações | ❌ | ❌ | ✅ |

## Endpoints principais

```
POST   /api/auth/login
GET    /api/candidates?q=&stage=&area=&page=
POST   /api/candidates
GET    /api/candidates/:id
PATCH  /api/candidates/:id/stage
GET    /api/jobs
POST   /api/interviews
POST   /api/interviews/invite          ← gerador WhatsApp
POST   /api/ai/analyze-cv              ← análise individual
POST   /api/ai/rank-cvs                ← ranking em lote (até 10)
POST   /api/ai/legal-analysis          ← LexAnalyzer
POST   /api/ai/analyze-transcript      ← idiomas
POST   /api/ai/whatsapp-message
GET    /api/analytics/dashboard
GET    /api/analytics/performance
GET    /api/analytics/executive
GET    /api/audit-logs
GET    /api/health
```

## Testes

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app --cov-report=html
```

## Deploy produção

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec backend flask db upgrade
docker compose -f docker-compose.prod.yml exec backend flask seed
```

## Arquitetura

```
routes/ (controllers)
  └─► services/ (regras de negócio)
        └─► repositories/ (SQLAlchemy)
              └─► models/ (entidades)
                    └─► PostgreSQL
```
