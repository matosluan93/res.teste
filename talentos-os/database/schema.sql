-- ===================================================
-- TalentOS · Schema PostgreSQL 16
-- ===================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- busca por similaridade

-- ── Enums ──────────────────────────────────────────
CREATE TYPE user_role AS ENUM ('recruiter','manager','executive');
CREATE TYPE candidate_stage AS ENUM ('triagem','entrevista_rh','tecnica','final','proposta','contratado','reprovado','banco_talentos');
CREATE TYPE platform_source AS ENUM ('LinkedIn','Gupy','Pandapé','Indique & Ganhe','Site','Headhunter','Banco de Talentos');
CREATE TYPE job_status AS ENUM ('ativa','pausada','critica','encerrada','preenchida');
CREATE TYPE job_urgency AS ENUM ('baixa','media','alta','critica');
CREATE TYPE interview_type AS ENUM ('entrevista_rh','tecnica_presencial','tecnica_video','banca_executiva','case_desafio','painel_time');
CREATE TYPE interview_status AS ENUM ('agendada','realizada','cancelada','reagendada','reprovado','aprovado');
CREATE TYPE invite_type AS ENUM ('convite_direto','pre_perguntas');
CREATE TYPE legal_status AS ENUM ('aprovado','reprovado','analise_humana','pendente');

-- ── Cells ──────────────────────────────────────────
CREATE TABLE cells (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(80) NOT NULL,
    icon        VARCHAR(10),
    color       VARCHAR(20),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Users ──────────────────────────────────────────
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(120) NOT NULL,
    email           VARCHAR(180) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            user_role NOT NULL DEFAULT 'recruiter',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    cell_id         INTEGER REFERENCES cells(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role  ON users(role);

-- ── Jobs ───────────────────────────────────────────
CREATE TABLE jobs (
    id                  SERIAL PRIMARY KEY,
    title               VARCHAR(150) NOT NULL,
    area                VARCHAR(80) NOT NULL,
    level               VARCHAR(60),
    location            VARCHAR(120),
    modality            VARCHAR(40),
    contract_type       VARCHAR(20),
    description         TEXT,
    requirements        JSONB DEFAULT '[]',
    salary_range_min    INTEGER,
    salary_range_max    INTEGER,
    headcount_approved  INTEGER NOT NULL DEFAULT 1,
    candidates_target   INTEGER NOT NULL DEFAULT 15,
    status              job_status NOT NULL DEFAULT 'ativa',
    urgency             job_urgency NOT NULL DEFAULT 'media',
    deadline            TIMESTAMPTZ,
    requires_language   BOOLEAN NOT NULL DEFAULT FALSE,
    required_language   VARCHAR(50),
    cell_id             INTEGER REFERENCES cells(id) ON DELETE SET NULL,
    recruiter_id        INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_jobs_status  ON jobs(status);
CREATE INDEX idx_jobs_area    ON jobs(area);
CREATE INDEX idx_jobs_urgency ON jobs(urgency);

-- ── Candidates ─────────────────────────────────────
CREATE TABLE candidates (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(120) NOT NULL,
    email               VARCHAR(180) NOT NULL,
    phone               VARCHAR(30),
    cpf                 VARCHAR(14),
    city                VARCHAR(100),
    linkedin_url        VARCHAR(255),
    current_role        VARCHAR(120),
    area                VARCHAR(80),
    education           VARCHAR(255),
    experience_years    INTEGER,
    skills              JSONB DEFAULT '[]',
    stage               candidate_stage NOT NULL DEFAULT 'triagem',
    source              platform_source,
    job_id              INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
    recruiter_id        INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ai_score            FLOAT,
    ai_fit_technical    FLOAT,
    ai_fit_cultural     FLOAT,
    main_language       VARCHAR(50),
    language_level      VARCHAR(20),
    language_score      FLOAT,
    disc_profile        JSONB,
    recruiter_notes     TEXT,
    is_talent_bank      BOOLEAN NOT NULL DEFAULT FALSE,
    salary_expectation  VARCHAR(60),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_cand_stage      ON candidates(stage);
CREATE INDEX idx_cand_area       ON candidates(area);
CREATE INDEX idx_cand_job        ON candidates(job_id);
CREATE INDEX idx_cand_name_trgm  ON candidates USING gin(name gin_trgm_ops);
CREATE INDEX idx_cand_cpf        ON candidates(cpf);

-- ── Interviews ─────────────────────────────────────
CREATE TABLE interviews (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id              INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
    interviewer_id      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    type                interview_type NOT NULL,
    status              interview_status NOT NULL DEFAULT 'agendada',
    scheduled_at        TIMESTAMPTZ,
    duration_minutes    INTEGER DEFAULT 60,
    meeting_link        VARCHAR(255),
    feedback            TEXT,
    feedback_score      SMALLINT CHECK (feedback_score BETWEEN 1 AND 5),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_int_candidate ON interviews(candidate_id);
CREATE INDEX idx_int_status    ON interviews(status);
CREATE INDEX idx_int_scheduled ON interviews(scheduled_at);

-- ── Interview Invites ──────────────────────────────
CREATE TABLE interview_invites (
    id                  SERIAL PRIMARY KEY,
    interview_id        INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    candidate_id        INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    recruiter_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invite_type         invite_type NOT NULL,
    whatsapp_number     VARCHAR(20),
    message_text        TEXT,
    whatsapp_url        TEXT,
    status              VARCHAR(20) NOT NULL DEFAULT 'enviado',
    sent_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at        TIMESTAMPTZ
);

-- ── Legal Analysis ─────────────────────────────────
CREATE TABLE legal_analyses (
    id                      SERIAL PRIMARY KEY,
    candidate_id            INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    analyst_id              INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    natcorp_data            TEXT,
    escavador_data          TEXT,
    other_platforms_data    TEXT,
    status                  legal_status NOT NULL DEFAULT 'pendente',
    verdict                 VARCHAR(60),
    reasoning               TEXT,
    full_report             TEXT,
    processes_count         INTEGER NOT NULL DEFAULT 0,
    has_criminal_record     BOOLEAN NOT NULL DEFAULT FALSE,
    has_active_process      BOOLEAN NOT NULL DEFAULT FALSE,
    requires_human_review   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_legal_status ON legal_analyses(status);

-- ── Language Assessments ───────────────────────────
CREATE TABLE language_assessments (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    assessor_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    language            VARCHAR(50) NOT NULL,
    cefr_level          VARCHAR(5),
    descriptive_level   VARCHAR(30),
    score_speaking      FLOAT,
    score_writing       FLOAT,
    score_listening     FLOAT,
    score_reading       FLOAT,
    score_vocabulary    FLOAT,
    score_grammar       FLOAT,
    score_fluency       FLOAT,
    score_overall       FLOAT,
    transcript          TEXT,
    recording_filename  VARCHAR(255),
    ai_analysis         JSONB,
    recommendation      VARCHAR(40),
    justification       TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── CV Analyses ────────────────────────────────────
CREATE TABLE cv_analyses (
    id                  SERIAL PRIMARY KEY,
    candidate_id        INTEGER REFERENCES candidates(id) ON DELETE SET NULL,
    job_id              INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
    analyst_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cv_text             TEXT,
    candidate_name_raw  VARCHAR(120),
    score_overall       FLOAT,
    fit_technical       FLOAT,
    fit_cultural        FLOAT,
    ai_result           JSONB,
    recommendation      VARCHAR(30),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Platforms ──────────────────────────────────────
CREATE TABLE platforms (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(60) NOT NULL UNIQUE,
    slug                VARCHAR(40) NOT NULL UNIQUE,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    color               VARCHAR(10),
    icon                VARCHAR(10),
    total_candidates    INTEGER NOT NULL DEFAULT 0,
    total_hired         INTEGER NOT NULL DEFAULT 0,
    avg_cost_per_hire   FLOAT,
    conversion_rate     FLOAT,
    active_jobs         INTEGER NOT NULL DEFAULT 0,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Cell Members ───────────────────────────────────
CREATE TABLE cell_members (
    id                  SERIAL PRIMARY KEY,
    cell_id             INTEGER NOT NULL REFERENCES cells(id) ON DELETE CASCADE,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    active_jobs_count   INTEGER NOT NULL DEFAULT 0,
    hires_count         INTEGER NOT NULL DEFAULT 0,
    sla_percentage      FLOAT,
    UNIQUE(cell_id, user_id)
);

-- ── Audit Logs ─────────────────────────────────────
CREATE TABLE audit_logs (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,
    resource    VARCHAR(80),
    resource_id INTEGER,
    detail      TEXT,
    meta        JSONB,
    ip_address  VARCHAR(45),
    user_agent  VARCHAR(255),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_audit_user    ON audit_logs(user_id);
CREATE INDEX idx_audit_action  ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);

-- ── Updated_at trigger ─────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_upd      BEFORE UPDATE ON users      FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_jobs_upd       BEFORE UPDATE ON jobs        FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_candidates_upd BEFORE UPDATE ON candidates  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_interviews_upd BEFORE UPDATE ON interviews  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_legal_upd      BEFORE UPDATE ON legal_analyses FOR EACH ROW EXECUTE FUNCTION update_updated_at();
