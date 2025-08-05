from datetime import timedelta, datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response, validate_authentication
from api.route_utils import RouteHelper, require_authentication
from repo.repositories import UsersRepository
from security.validators import SecurityValidator
from services.authentication.auth_service import AuthService
from services.authentication.user_model import User
from services.authorization.authorization import get_current_user

router = APIRouter(
    tags=['auth'],
    prefix='/auth'
)


class UserRoleData(BaseModel):
    uid: str
    role: str


@router.post("/login")
async def login(
        user_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
        auth_service: AuthService = Depends(get_service_by_type(AuthService))
) -> JSONResponse:
    try:
        # Validate @forvia email domain
        if not user_data.username or '@forvia' not in user_data.username.lower():
            raise create_error_response(
                operation="authenticate",
                entity_type="User",
                entity_id=user_data.username,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                custom_message="Only @forvia email addresses are allowed"
            )
        
        user_status, user, auth_result = auth_service.is_authenticated(user_data.username, user_data.password)
        if user_status:
            token_data = {"username": user["username"], "level": user["level"]}
            expires = datetime.utcnow() + timedelta(seconds=28800)
            token_data.update({"exp": expires})
            secret = auth_service.get_secret()
            token = jwt.encode(token_data, secret, algorithm="HS256")

            response = JSONResponse(status_code=status.HTTP_200_OK, content={
                'access_token': token
            })

            response.headers["User-Data"] = user["username"]
            response.headers["Level"] = user["level"]
            response.headers["Token-Expiration"] = "28800"
            return response
        else:
            # Provide specific error messages based on authentication failure reason
            if auth_result == "user_not_found":
                error_message = "No account found with this email address"
                status_code = status.HTTP_404_NOT_FOUND
            elif auth_result == "invalid_password":
                error_message = "Invalid password"
                status_code = status.HTTP_401_UNAUTHORIZED
            else:
                error_message = "Invalid credentials provided"
                status_code = status.HTTP_401_UNAUTHORIZED
            
            raise create_error_response(
                operation="authenticate",
                entity_type="User",
                entity_id=user_data.username,
                status_code=status_code,
                custom_message=error_message
            )
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="authenticate",
            entity_type="User",
            entity_id=user_data.username,
            exception=e
        )


@router.post("/create_user")
async def create_user(
        user: User,
        auth_service: AuthService = Depends(get_service_by_type(AuthService)),
        users_repository: UsersRepository = Depends(get_service_by_type(UsersRepository))
) -> JSONResponse:
    try:
        # Validate @forvia email domain
        if not user.username or '@forvia' not in user.username.lower():
            raise create_error_response(
                operation="create_user",
                entity_type="User",
                entity_id=user.username,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                custom_message="Only @forvia email addresses are allowed"
            )
        
        print(f"Creating user: {user.username} with uid: {user.uid}")
        
        # Set default level if empty
        if not user.level or user.level == '':
            user.level = 'operator'
        
        # Hash the password
        hashed_password = auth_service.hash_password(user.password)
        user.password = hashed_password
        
        print(f"Attempting to create user in database...")
        users_repository.create(user)
        print(f"User created successfully!")

        # Generate token
        token_data = {"username": user.username, "level": user.level}
        expires = datetime.utcnow() + timedelta(seconds=28800)
        token_data.update({"exp": expires})
        secret = auth_service.get_secret()
        token = jwt.encode(token_data, secret, algorithm="HS256")

        response = JSONResponse(status_code=status.HTTP_201_CREATED, content={
            'access_token': token
        })

        response.headers["User-Data"] = user.username
        response.headers["Level"] = user.level
        response.headers["Token-Expiration"] = "28800"
        return response
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating user: {e}")
        import traceback
        traceback.print_exc()
        raise create_error_response(
            operation="create",
            entity_type="User",
            entity_id=user.username,
            exception=e
        )


@router.post("/update_role")
async def update_users_role(
        user_data: UserRoleData,
        user: Dict[str, Any] = Depends(require_authentication("update user role")),
        users_repository: UsersRepository = Depends(get_service_by_type(UsersRepository))
) -> JSONResponse:
    # Check admin authorization
    if user.get("level") != "admin":
        raise create_error_response(
            operation="update role",
            entity_type="User",
            entity_id=user_data.uid,
            status_code=status.HTTP_403_FORBIDDEN,
            custom_message="Admin privileges required to update user roles"
        )
    
    try:
        users_repository.update_role(user_data.role, user_data.uid)
        return RouteHelper.create_success_response(
            f"User {user_data.uid} role updated to {user_data.role} successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="update role",
            entity_type="User",
            entity_id=user_data.uid,
            exception=e
        )


@router.get("/users")
async def get_users(
        users_repository: UsersRepository = Depends(get_service_by_type(UsersRepository))
) -> list:
    try:
        return RouteHelper.list_entities(users_repository, "User")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="list",
            entity_type="User",
            exception=e
        )


@router.get("/roles")
async def get_available_roles() -> list:
    """Get list of available user roles."""
    try:
        return ["technician", "operator"]
    except Exception as e:
        raise create_error_response(
            operation="retrieve",
            entity_type="User roles",
            exception=e
        )
