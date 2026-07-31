from src.shared.application.uow import UnitOfWork

from .dtos import WorkflowResponse
from .repos import WorkflowRepository


class WorkflowEditorService:
    def __init__(self, uow: UnitOfWork, workflow_repo: WorkflowRepository) -> None:
        self.uow = uow
        self.workflow_repo = workflow_repo

    async def create(self) -> WorkflowResponse: ...
