from src.shared.infra.repos import SqlAlchemyRepository

from ..domain.entities import Workflow
from .mappers import WorkflowMapper
from .models import WorkflowOrm


class SqlWorkflowRepository(SqlAlchemyRepository[Workflow, WorkflowOrm]):
    model = WorkflowOrm
    model_mapper = WorkflowMapper
