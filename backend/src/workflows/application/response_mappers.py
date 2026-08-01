from src.workflows.domain.entities import Status, Transition, Workflow

from .dtos import StatusResponse, TransitionResponse, WorkflowResponse


def map_status_to_response(status: Status) -> StatusResponse:
    return StatusResponse(
        id=status.id,
        created_at=status.created_at,
        updated_at=status.updated_at,
        name=status.name,
        description=status.description,
        color=status.color,
        category=status.category,
        kind=status.kind,
        order=status.order,
    )


def map_transition_to_response(transition: Transition) -> TransitionResponse:
    return TransitionResponse(
        id=transition.id,
        created_at=transition.created_at,
        updated_at=transition.updated_at,
        sources=transition.sources,
        destination=transition.destination,
        guards=list(transition.guards),
        actions=list(transition.actions),
    )


def map_workflow_to_response(workflow: Workflow) -> WorkflowResponse:
    return WorkflowResponse(
        id=workflow.id,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        name=workflow.name,
        description=workflow.description,
        is_default=workflow.is_default,
        is_active=workflow.is_active,
        version=workflow.version,
        author_id=workflow.author_id,
        initial_status_id=workflow.initial_status_id,
        statuses=[map_status_to_response(status) for status in workflow.statuses],
        transitions=[
            map_transition_to_response(transition) for transition in workflow.transitions
        ],
    )
