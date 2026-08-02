from fastapi import APIRouter, status

from src.iam.application.dtos import LoginResponse, TokenRequest, TokensResponse, UserCredentials

router = APIRouter(prefix="/auth", tags=["Аутентификация | Auth"])


@router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    summary="Проверка личности",
)
async def login(credentials: UserCredentials) -> LoginResponse: ...


@router.post(
    path="/token",
    status_code=status.HTTP_200_OK,
    response_model=TokensResponse,
    summary="Получить пару токенов",
)
async def get_token(request: TokenRequest) -> TokensResponse: ...
