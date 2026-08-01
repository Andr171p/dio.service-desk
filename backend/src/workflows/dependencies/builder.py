from typing import Annotated

from fastapi import Depends

from src.workflows.application.builder import WorkflowBuilder

from .base import WorkflowRepoDep, WorkflowTransactionDep


def get_workflow_builder(
        workflow_repo: WorkflowRepoDep, transaction: WorkflowTransactionDep,
) -> WorkflowBuilder:
    return WorkflowBuilder(workflow_repo=workflow_repo, transaction=transaction)


WorkflowBuilderDep = Annotated[WorkflowBuilder, Depends(get_workflow_builder)]
