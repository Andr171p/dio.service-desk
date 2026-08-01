from typing import Annotated

from fastapi import Depends

from src.shared.application.transaction import Transaction
from src.shared.dependencies import EventPublisherDep, SessionDep, multi_level_cache
from src.shared.infra.cache import CachedRepository
from src.workflows.application.repos import WorkflowRepository
from src.workflows.domain.entities import Workflow
from src.workflows.infra.repos import SqlWorkflowRepository


def get_workflow_transaction(
        session: SessionDep, event_publisher: EventPublisherDep,
) -> Transaction[Workflow]:
    return Transaction[Workflow](session, event_publisher)


def get_workflow_repo(session: SessionDep) -> SqlWorkflowRepository:
    return SqlWorkflowRepository(session)


def get_cached_workflow_repo(
        workflow_repo: WorkflowRepository = Depends(get_workflow_repo),
) -> CachedRepository[Workflow]:
    return CachedRepository[Workflow](workflow_repo, multi_level_cache, prefix="wfs")


WorkflowRepoDep = Annotated[WorkflowRepository, Depends(get_cached_workflow_repo)]
WorkflowTransactionDep = Annotated[Transaction[Workflow], Depends(get_workflow_transaction)]

__all__ = ["WorkflowRepoDep", "WorkflowTransactionDep"]
