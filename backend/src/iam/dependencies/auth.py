from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.iam.application.dtos import Identity
from src.iam.application.services import blacklist
from src.iam.domain.exceptions import UnauthorizedError
from src.iam.security import decode_token
from src.shared.infra.cache import Cache

http_bearer = HTTPBearer(auto_error=False)


def _build_identity_from_payload(payload: dict[str, Any]) -> Identity:
    ...


async def get_current_identity(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
        cache: Cache[bool] = Depends(...),
) -> Identity:
    if credentials is None:
        raise UnauthorizedError("Authorization header is missing.")

    payload = decode_token(credentials.credentials)

    jti = payload.get("jti")
    if jti is None:
        raise UnauthorizedError("Missing required jti claim.")

    if await blacklist.is_revoked(jti, cache):
        raise UnauthorizedError("Token was revoked.")

    return _build_identity_from_payload(payload)


CurrentIdentity = Annotated[Identity, Depends(get_current_identity)]
