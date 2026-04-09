-- Configurações iniciais do PostgreSQL para TalentOS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
-- O schema principal é criado via Flask-Migrate (Alembic)
