import json
from flask import current_app
import anthropic

LEX_SYSTEM = """Você é o LexAnalyzer, um sistema especialista em análise de risco jurídico, reputacional e trabalhista para a Stefanini.
Todas as regras têm caráter OBRIGATÓRIO.

REGRA Nº 1 (PRIORIDADE ABSOLUTA): QUALQUER processo trabalhista cujo assunto NÃO esteja claramente relacionado a verbas rescisórias DEVE gerar REPROVAÇÃO AUTOMÁTICA.

EXCEÇÃO ÚNICA para APROVAÇÃO — TODAS as condições simultâneas:
1. Candidato é AUTOR (reclamante).
2. Processo TRABALHISTA exclusivamente de verbas rescisórias.
3. NÃO menciona: assédio, dano moral, indenização, conduta.
4. Processo NÃO está ativo.
5. Sem divergências entre plataformas.
6. Nenhum outro processo de qualquer tipo.

REPROVAÇÃO AUTOMÁTICA:
- Processo trabalhista como réu/reclamado.
- Processos criminais (ativos ou arquivados).
- Qualquer processo ativo.
- 5+ ações trabalhistas.
- Divergência entre plataformas.
- Processo com assédio, dano moral, indenização, conduta.
- Natcorp: "baixa performance","não indicado","problemas de conduta".

ANÁLISE HUMANA NECESSÁRIA: processos cíveis, dados incompletos, inconsistências.

HIERARQUIA FINAL:
1º REPROVAÇÃO → 🔴 REPROVADO
2º EXCEÇÃO ÚNICA → 🟢 APROVADO
3º DADOS INCOMPLETOS → ⚠️ ANÁLISE HUMANA NECESSÁRIA

Responda APENAS em JSON:
{"parecer":"APROVADO|REPROVADO|ANALISE_HUMANA","emoji":"🟢|🔴|⚠️","resumo_natcorp":"...","resumo_escavador":"...","resumo_outras":"...","processos_encontrados":0,"processos":[{"numero":"","natureza":"","papel":"","assunto":"","tribunal":"","status":""}],"motivos":["..."],"requer_link_juridico":false,"full_report":"texto completo formatado"}"""

class AIService:
    def _get_client(self):
        return anthropic.Anthropic(api_key=current_app.config["ANTHROPIC_API_KEY"])

    def analyze_cv(self, cv_text: str, job_description: str = "") -> dict:
        client = self._get_client()
        prompt = f"""Analise este currículo para a vaga: {job_description or "posição em aberto"}.
Retorne SOMENTE JSON sem markdown:
{{"nome":"","cargo_atual":"","resumo":"2 frases","score_geral":0,"experiencia_anos":0,"formacao":"","pontos_fortes":["","",""],"pontos_atencao":["",""],"idiomas":[{{"idioma":"","nivel":"","score":0}}],"competencias":["","","","",""],"fit_cultural":0,"fit_tecnico":0,"fit_lideranca":0,"recomendacao":"Avançar|Avaliar|Não recomendado","motivo":"1 frase"}}
CURRÍCULO:
{cv_text}"""
        msg = client.messages.create(
            model=current_app.config["ANTHROPIC_MODEL"],
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = msg.content[0].text.replace("```json","").replace("```","").strip()
        return json.loads(raw)

    def rank_cvs(self, job_description: str, cvs: list[dict]) -> dict:
        client = self._get_client()
        cvs_text = "\n\n".join(
            f"=== CANDIDATO {i + 1}: {candidate['name']} ===\n{candidate['text']}"
            for i, candidate in enumerate(cvs)
        )
        prompt = f"""Analise {len(cvs)} currículos para a vaga e gere ranking. Retorne SOMENTE JSON:
{{"vaga_resumida":"","ranking":[{{"posicao":1,"nome":"","score":0,"fit_tecnico":0,"fit_cultural":0,"experiencia":"","pontos_fortes":[""],"pontos_atencao":[""],"justificativa":"2-3 frases","recomendacao":"Avançar|Avaliar|Não recomendado"}}]}}
VAGA: {job_description}
CURRÍCULOS: {cvs_text}"""
        msg = client.messages.create(
            model=current_app.config["ANTHROPIC_MODEL"],
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = msg.content[0].text.replace("```json","").replace("```","").strip()
        return json.loads(raw)

    def legal_analysis(self, nome: str, cpf: str, vaga: str, natcorp: str, escavador: str, outras: str) -> dict:
        client = self._get_client()
        user_msg = f"Nome: {nome}\nCPF: {cpf}\nVaga: {vaga}\nNatcorp: \"{natcorp}\"\nEscavador: \"{escavador}\"\nOutras: \"{outras}\""
        msg = client.messages.create(
            model=current_app.config["ANTHROPIC_MODEL"],
            max_tokens=1500,
            system=LEX_SYSTEM,
            messages=[{"role": "user", "content": user_msg}]
        )
        raw = msg.content[0].text.replace("```json","").replace("```","").strip()
        return json.loads(raw)

    def analyze_transcript(self, transcript: str, language: str, candidate_name: str) -> dict:
        client = self._get_client()
        prompt = f"""Avalie a proficiência em {language} do candidato {candidate_name}. Retorne SOMENTE JSON:
{{"nivel_cefr":"","nivel_descritivo":"","scores":{{"speaking":0,"vocabulario":0,"gramatica":0,"fluencia":0,"coerencia":0}},"score_geral":0,"pontos_fortes":[""],"pontos_melhoria":[""],"parecer":"Recomendado|Recomendado com ressalvas|Não recomendado","justificativa":"2-3 frases"}}
TRANSCRIÇÃO: {transcript}"""
        msg = client.messages.create(
            model=current_app.config["ANTHROPIC_MODEL"],
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = msg.content[0].text.replace("```json","").replace("```","").strip()
        return json.loads(raw)

    def generate_whatsapp_message(self, recruiter_name: str, job_title: str, candidate_name: str,
                                   phone: str, invite_type: str) -> dict:
        phone_clean = "".join(filter(str.isdigit, phone))
        wa_phone = "55" + phone_clean
        if invite_type == "direto":
            msg = (f"Olá {candidate_name}, tudo bem?\n\nSou {recruiter_name}, do time de Recrutamento & Seleção da Stefanini.\n"
                   f"Recebemos seu currículo para a oportunidade de *{job_title}* e gostaríamos de te convidar para "
                   f"participar de nossa Entrevista Técnica.\n\nEntraremos em contato por este número para agendar a entrevista técnica.\n"
                   f"Se tiver qualquer dúvida ou precisar de apoio, estou à disposição.\nConte conosco!\n\nAtenciosamente,\nEquipe de Gente e Cultura")
        else:
            msg = (f"Olá {candidate_name}, tudo bem?\n\nSou {recruiter_name}, do time de People & Performance da Stefanini.\n"
                   f"Recebemos seu currículo para a oportunidade de *{job_title}* e gostaríamos de te convidar.\n\n"
                   f"Antes de seguirmos, gostaria de confirmar:\n1 - Disponibilidade híbrida ou presencial?\n"
                   f"2 - Pretensão salarial?\n3 - Preferência CLT ou PJ?\n4 - Disponibilidade para entrevista via Teams?\n\n"
                   f"Fico no aguardo!\n\nAtenciosamente,\nEquipe de Gente e Cultura")
        wa_url = f"https://wa.me/{wa_phone}?text={__import__('urllib.parse', fromlist=['quote']).quote(msg)}"
        return {"message": msg, "whatsapp_url": wa_url, "phone": wa_phone}

ai_service = AIService()
