from flask import Blueprint, request, jsonify, g
from ..middleware.auth import login_required
from ..services.ai_service import ai_service
from ..services.audit_service import audit_service
from ..extensions import db
from ..models.assessment import LegalAnalysis, LegalStatus, LanguageAssessment, CVAnalysis
from ..extensions import limiter

ai_bp = Blueprint("ai", __name__)

@ai_bp.post("/analyze-cv")
@login_required
@limiter.limit("30 per hour")
def analyze_cv():
    data = request.get_json() or {}
    cv_text = data.get("cv_text", "").strip()
    if len(cv_text) < 50:
        return jsonify({"error": "validation_error", "message": "Currículo muito curto"}), 422
    try:
        result = ai_service.analyze_cv(cv_text, data.get("job_description", ""))
        analysis = CVAnalysis(
            candidate_id=data.get("candidate_id"),
            job_id=data.get("job_id"),
            analyst_id=g.current_user.id,
            cv_text=cv_text,
            candidate_name_raw=result.get("nome"),
            score_overall=result.get("score_geral"),
            fit_technical=result.get("fit_tecnico"),
            fit_cultural=result.get("fit_cultural"),
            ai_result=result,
            recommendation=result.get("recomendacao"),
        )
        db.session.add(analysis)
        db.session.commit()
        audit_service.log(g.current_user.id, "cv_analyzed", "cv_analysis", analysis.id, f"CV de {result.get('nome','?')} analisado")
        return jsonify({"analysis_id": analysis.id, "result": result}), 200
    except Exception as e:
        return jsonify({"error": "ai_error", "message": str(e)}), 500

@ai_bp.post("/rank-cvs")
@login_required
@limiter.limit("10 per hour")
def rank_cvs():
    data = request.get_json() or {}
    job_desc = data.get("job_description", "").strip()
    cvs = data.get("cvs", [])
    if not job_desc:
        return jsonify({"error": "validation_error", "message": "job_description é obrigatório"}), 422
    if len(cvs) < 2:
        return jsonify({"error": "validation_error", "message": "Mínimo de 2 currículos"}), 422
    if len(cvs) > 10:
        return jsonify({"error": "validation_error", "message": "Máximo de 10 currículos"}), 422
    try:
        result = ai_service.rank_cvs(job_desc, cvs)
        audit_service.log(g.current_user.id, "cvs_ranked", None, None, f"Ranking gerado: {len(cvs)} candidatos")
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "ai_error", "message": str(e)}), 500

@ai_bp.post("/legal-analysis")
@login_required
@limiter.limit("20 per hour")
def legal_analysis():
    data = request.get_json() or {}
    nome = data.get("nome", "").strip()
    cpf = data.get("cpf", "").strip()
    if not nome or not cpf:
        return jsonify({"error": "validation_error", "message": "Nome e CPF são obrigatórios"}), 422
    try:
        result = ai_service.legal_analysis(
            nome=nome, cpf=cpf, vaga=data.get("vaga",""),
            natcorp=data.get("natcorp",""), escavador=data.get("escavador",""),
            outras=data.get("outras",""),
        )
        status_map = {"APROVADO": LegalStatus.APROVADO, "REPROVADO": LegalStatus.REPROVADO, "ANALISE_HUMANA": LegalStatus.ANALISE_HUMANA}
        analysis = LegalAnalysis(
            candidate_id=data.get("candidate_id"),
            analyst_id=g.current_user.id,
            natcorp_data=data.get("natcorp"),
            escavador_data=data.get("escavador"),
            other_platforms_data=data.get("outras"),
            status=status_map.get(result.get("parecer"), LegalStatus.ANALISE_HUMANA),
            verdict=result.get("emoji"),
            reasoning="; ".join(result.get("motivos", [])),
            full_report=result.get("full_report"),
            processes_count=result.get("processos_encontrados", 0),
        ) if data.get("candidate_id") else None
        if analysis:
            db.session.add(analysis)
            db.session.commit()
        audit_service.log(g.current_user.id, "legal_analyzed", "legal_analysis", None, f"Análise jurídica: {nome} → {result.get('emoji')}")
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "ai_error", "message": str(e)}), 500

@ai_bp.post("/analyze-transcript")
@login_required
@limiter.limit("20 per hour")
def analyze_transcript():
    data = request.get_json() or {}
    transcript = data.get("transcript", "").strip()
    if len(transcript) < 50:
        return jsonify({"error": "validation_error", "message": "Transcrição muito curta"}), 422
    try:
        result = ai_service.analyze_transcript(transcript, data.get("language","Inglês"), data.get("candidate_name","Candidato"))
        scores = result.get("scores", {})
        assessment = LanguageAssessment(
            candidate_id=data.get("candidate_id"),
            assessor_id=g.current_user.id,
            language=data.get("language","Inglês"),
            cefr_level=result.get("nivel_cefr"),
            descriptive_level=result.get("nivel_descritivo"),
            score_speaking=scores.get("speaking"),
            score_writing=None,
            score_listening=None,
            score_reading=None,
            score_vocabulary=scores.get("vocabulario"),
            score_grammar=scores.get("gramatica"),
            score_fluency=scores.get("fluencia"),
            score_overall=result.get("score_geral"),
            transcript=transcript,
            ai_analysis=result,
            recommendation=result.get("parecer"),
            justification=result.get("justificativa"),
        ) if data.get("candidate_id") else None
        if assessment:
            db.session.add(assessment)
            db.session.commit()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "ai_error", "message": str(e)}), 500

@ai_bp.post("/whatsapp-message")
@login_required
def whatsapp_message():
    data = request.get_json() or {}
    required = ["recruiter_name","job_title","candidate_name","phone","invite_type"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": "validation_error", "message": f"Campos obrigatórios: {missing}"}), 422
    result = ai_service.generate_whatsapp_message(**{k: data[k] for k in required})
    return jsonify(result), 200
