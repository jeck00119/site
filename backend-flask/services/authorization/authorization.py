from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status

from api.dependencies.services import get_service_by_type
from services.authentication.auth_service import AuthService

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
        token: str = Depends(oauth2_bearer),
        auth_service: AuthService = Depends(get_service_by_type(AuthService))
):
    try:
        payload = jwt.decode(token, auth_service.get_secret(), algorithms="HS256")
        username: str = payload.get("username")
        level: str = payload.get("level")

        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

        return {"username": username, "level": level}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
