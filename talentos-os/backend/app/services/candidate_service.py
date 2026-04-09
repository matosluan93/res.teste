from ..repositories.candidate_repo import CandidateRepository
from ..models.candidate import Candidate
from ..extensions import db

candidate_repo = CandidateRepository()

class CandidateService:
    def list_candidates(self, filters: dict, page: int = 1, per_page: int = 20) -> dict:
        return candidate_repo.search(
            query=filters.get("q"),
            stage=filters.get("stage"),
            area=filters.get("area"),
            source=filters.get("source"),
            score_min=filters.get("score_min"),
            page=page,
            per_page=per_page,
        )

    def get_candidate(self, id: int) -> Candidate:
        candidate = candidate_repo.get_by_id(id)
        if not candidate:
            raise ValueError("Candidato não encontrado")
        return candidate

    def create_candidate(self, data: dict, recruiter_id: int) -> Candidate:
        data["recruiter_id"] = recruiter_id
        candidate = candidate_repo.create(**data)
        candidate_repo.save()
        return candidate

    def update_candidate(self, id: int, data: dict) -> Candidate:
        candidate = self.get_candidate(id)
        candidate_repo.update(candidate, **data)
        candidate_repo.save()
        return candidate

    def advance_stage(self, id: int, stage: str) -> Candidate:
        candidate = self.get_candidate(id)
        candidate_repo.update(candidate, stage=stage)
        candidate_repo.save()
        return candidate

    def delete_candidate(self, id: int) -> None:
        candidate = self.get_candidate(id)
        candidate_repo.delete(candidate)
        candidate_repo.save()

    def get_pipeline_board(self) -> dict:
        from ..models.candidate import CandidateStage
        board = {}
        for stage in CandidateStage:
            items = candidate_repo.get_by_stage(stage)
            board[stage.value] = [c.to_dict() for c in items]
        return board

candidate_service = CandidateService()
