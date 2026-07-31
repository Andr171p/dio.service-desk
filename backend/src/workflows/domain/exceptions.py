from fastapi import status

from src.shared.domain.exceptions import AppError


class DuplicateStatusError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "DUPLICATE_STATUS_ERROR"
    public_message = "Статус внутри Workflow должен быть уникальным"


class InvalidWorkflowError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "INVALID_WORKFLOW_ERROR"
    public_message = "Невалидное состояние Workflow"


class WorkflowConfigurationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "WORKFLOW_CONFIGURATION_ERROR"
    public_message = "Ошибка при конфигурации Workflow"
