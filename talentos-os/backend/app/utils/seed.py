from ..extensions import db
from ..models.user import User, UserRole
from ..models.platform import Platform
from ..models.cell import Cell, CellMember
from ..models.job import Job, JobStatus, JobUrgency

def run_seeds():
    _seed_users()
    _seed_platforms()
    _seed_cells()
    _seed_jobs()
    db.session.commit()
    print("✅ Seeds executados com sucesso")

def _seed_users():
    if db.session.scalar(db.select(User.id).limit(1)):
        return
    users = [
        {"name":"Ana Lima","email":"ana.lima@stefanini.com","password":"Admin@2025","role":UserRole.EXECUTIVE},
        {"name":"Fernanda Costa","email":"fernanda.costa@stefanini.com","password":"Manager@2025","role":UserRole.MANAGER},
        {"name":"Carlos Mendes","email":"carlos.mendes@stefanini.com","password":"Recruiter@2025","role":UserRole.RECRUITER},
        {"name":"Roberto Farias","email":"roberto.farias@stefanini.com","password":"Recruiter@2025","role":UserRole.RECRUITER},
        {"name":"Demo","email":"demo@talentos.com","password":"demo123","role":UserRole.EXECUTIVE},
    ]
    for u in users:
        user = User(name=u["name"], email=u["email"], role=u["role"], is_active=True)
        user.set_password(u["password"])
        db.session.add(user)
    print("   → Usuários criados")

def _seed_platforms():
    if db.session.scalar(db.select(Platform.id).limit(1)):
        return
    platforms = [
        {"name":"Indique & Ganhe","slug":"indicacao","color":"#C9973A","icon":"🏆","total_candidates":38,"total_hired":11,"avg_cost_per_hire":4200,"conversion_rate":7.2,"active_jobs":6},
        {"name":"Gupy","slug":"gupy","color":"#4338CA","icon":"G","total_candidates":95,"total_hired":9,"avg_cost_per_hire":8800,"conversion_rate":3.1,"active_jobs":12},
        {"name":"Pandapé","slug":"pandape","color":"#FF6B35","icon":"P","total_candidates":64,"total_hired":6,"avg_cost_per_hire":9500,"conversion_rate":2.8,"active_jobs":7},
        {"name":"LinkedIn Jobs","slug":"linkedin","color":"#0077B5","icon":"in","total_candidates":50,"total_hired":8,"avg_cost_per_hire":14200,"conversion_rate":4.0,"active_jobs":8},
    ]
    for p in platforms:
        db.session.add(Platform(**p))
    print("   → Plataformas criadas")

def _seed_cells():
    if db.session.scalar(db.select(Cell.id).limit(1)):
        return
    db.session.add(Cell(name="Célula Tech", icon="💻", color="#3B7AF5"))
    db.session.add(Cell(name="Célula Business", icon="📊", color="#C9973A"))
    print("   → Células criadas")

def _seed_jobs():
    if db.session.scalar(db.select(Job.id).limit(1)):
        return
    jobs = [
        {"title":"Engenheiro(a) Sênior Backend","area":"Tecnologia","level":"Sênior","location":"São Paulo / Híbrido","modality":"hibrido","contract_type":"CLT","status":JobStatus.ATIVA,"urgency":JobUrgency.ALTA,"candidates_target":30,"requires_language":True,"required_language":"Inglês"},
        {"title":"Head de Marketing Digital","area":"Marketing","level":"Liderança","location":"Rio de Janeiro","modality":"presencial","contract_type":"CLT","status":JobStatus.ATIVA,"urgency":JobUrgency.MEDIA,"candidates_target":20},
        {"title":"CFO / Diretor Financeiro","area":"Financeiro","level":"C-Level","location":"São Paulo","modality":"presencial","contract_type":"CLT","status":JobStatus.ATIVA,"urgency":JobUrgency.ALTA,"candidates_target":15,"requires_language":True,"required_language":"Inglês"},
        {"title":"VP de Vendas","area":"Comercial","level":"C-Level","location":"São Paulo","modality":"presencial","contract_type":"CLT","status":JobStatus.CRITICA,"urgency":JobUrgency.CRITICA,"candidates_target":15},
        {"title":"Tech Lead — Cloud","area":"Tecnologia","level":"Sênior","location":"Remoto","modality":"remoto","contract_type":"CLT","status":JobStatus.ATIVA,"urgency":JobUrgency.ALTA,"candidates_target":25,"requires_language":True,"required_language":"Inglês"},
    ]
    for j in jobs:
        db.session.add(Job(**j))
    print("   → Vagas criadas")
