"""
Route Utilities

Common utilities and patterns for API routes to reduce code duplication.
"""

from typing import Any, Dict, List, Optional, Callable
from fastapi import Depends, HTTPException, status
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response, validate_authentication
from services.authorization.authorization import get_current_user
from repo.repository_exceptions import UidNotFound, UidNotUnique

class RouteHelper:
    """Helper class for common route operations."""
    
    @staticmethod
    def create_success_response(
        message: str,
        data: Any = None,
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """Create a standardized success response."""
        content = {"status": "success", "message": message}
        if data is not None:
            content["data"] = data
        return JSONResponse(status_code=status_code, content=content)
    
    @staticmethod
    def get_entity_by_id(repository, entity_uid: str, entity_type: str = "Entity"):
        """Get entity by ID with standardized error handling."""
        try:
            return repository.read_id(entity_uid)
        except UidNotFound:
            raise create_error_response(
                operation="retrieve",
                entity_type=entity_type,
                entity_id=entity_uid,
                exception=UidNotFound(f"{entity_type} not found")
            )
        except Exception as e:
            raise create_error_response(
                operation="retrieve",
                entity_type=entity_type,
                entity_id=entity_uid,
                exception=e
            )
    
    @staticmethod
    def create_entity(repository, entity_data, entity_type: str = "Entity"):
        """Create entity with standardized error handling. Accepts model or dict."""
        try:
            # Handle both model objects and dictionaries
            if hasattr(entity_data, 'uid'):
                # It's a model object
                uid = entity_data.uid
                repository.create(entity_data)
            else:
                # It's a dictionary - create temporary model-like object
                uid = entity_data.get('uid', 'unknown')
                
                class TempModel:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                    
                    def model_dump(self):
                        return {key: value for key, value in self.__dict__.items()}
                
                temp_model = TempModel(entity_data)
                repository.create(temp_model)
            
            return RouteHelper.create_success_response(
                f"{entity_type} {uid} created successfully",
                status_code=status.HTTP_201_CREATED
            )
        except UidNotUnique:
            uid = getattr(entity_data, 'uid', entity_data.get('uid', 'unknown') if isinstance(entity_data, dict) else 'unknown')
            raise create_error_response(
                operation="create",
                entity_type=entity_type,
                entity_id=uid,
                exception=UidNotUnique(f"{entity_type} already exists")
            )
        except Exception as e:
            uid = getattr(entity_data, 'uid', entity_data.get('uid', 'unknown') if isinstance(entity_data, dict) else 'unknown')
            raise create_error_response(
                operation="create",
                entity_type=entity_type,
                entity_id=uid,
                exception=e
            )
    
    @staticmethod
    def update_entity(repository, entity_data, entity_type: str = "Entity"):
        """Update entity with standardized error handling. Accepts model or dict."""
        try:
            # Handle both model objects and dictionaries
            if hasattr(entity_data, 'uid'):
                # It's a model object
                uid = entity_data.uid
                repository.update(entity_data)
            else:
                # It's a dictionary - create temporary model-like object
                uid = entity_data.get('uid', 'unknown')
                
                class TempModel:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                    
                    def model_dump(self):
                        return {key: value for key, value in self.__dict__.items()}
                
                temp_model = TempModel(entity_data)  
                repository.update(temp_model)
            
            return RouteHelper.create_success_response(
                f"{entity_type} {uid} updated successfully"
            )
        except UidNotFound:
            uid = getattr(entity_data, 'uid', entity_data.get('uid', 'unknown') if isinstance(entity_data, dict) else 'unknown')
            raise create_error_response(
                operation="update",
                entity_type=entity_type,
                entity_id=uid,
                exception=UidNotFound(f"{entity_type} not found")
            )
        except Exception as e:
            uid = getattr(entity_data, 'uid', entity_data.get('uid', 'unknown') if isinstance(entity_data, dict) else 'unknown')
            raise create_error_response(
                operation="update",
                entity_type=entity_type,
                entity_id=uid,
                exception=e
            )
    
    @staticmethod
    def delete_entity(repository, entity_uid: str, entity_type: str = "Entity"):
        """Delete entity with standardized error handling."""
        try:
            repository.delete(entity_uid)
            return RouteHelper.create_success_response(
                f"{entity_type} {entity_uid} deleted successfully"
            )
        except UidNotFound:
            raise create_error_response(
                operation="delete",
                entity_type=entity_type,
                entity_id=entity_uid,
                exception=UidNotFound(f"{entity_type} not found")
            )
        except Exception as e:
            raise create_error_response(
                operation="delete",
                entity_type=entity_type,
                entity_id=entity_uid,
                exception=e
            )
    
    @staticmethod
    def list_entities(repository, entity_type: str = "Entity") -> List[Dict]:
        """List all entities with standardized error handling."""
        try:
            return repository.read_all()
        except Exception as e:
            raise create_error_response(
                operation="list",
                entity_type=entity_type,
                exception=e
            )
    
    @staticmethod
    def transform_list_to_uid_name(items: List[Dict], default_name: str = "Unknown") -> List[Dict[str, str]]:
        """Transform list of entities to standardized uid/name format."""
        return [
            {
                'uid': item['uid'], 
                'name': item.get('name', default_name)
            } 
            for item in items
        ]

# Common dependency injection patterns
def get_authenticated_user():
    """Get authenticated user with standardized error handling."""
    def _get_user(user: dict = Depends(get_current_user)):
        validate_authentication(user)
        return user
    return _get_user

def require_authentication(operation: str = "perform this operation"):
    """Dependency that requires authentication."""
    def _require_auth(user: dict = Depends(get_current_user)):
        validate_authentication(user, operation)
        return user
    return _require_auth

# Standard CRUD route factories
def create_list_route(repository_class, entity_type: str):
    """Create a standard list route."""
    async def list_route(
        repository=Depends(get_service_by_type(repository_class))
    ):
        return RouteHelper.list_entities(repository, entity_type)
    return list_route

def create_get_route(repository_class, entity_type: str, model_class):
    """Create a standard get by ID route."""
    async def get_route(
        entity_uid: str,
        repository=Depends(get_service_by_type(repository_class))
    ):
        entity_data = RouteHelper.get_entity_by_id(repository, entity_uid, entity_type)
        return model_class(**entity_data)
    return get_route

def create_post_route(repository_class, service_class, entity_type: str, model_class):
    """Create a standard post route."""
    async def post_route(
        entity: model_class,
        user: dict = Depends(require_authentication(f"create {entity_type.lower()}")),
        repository=Depends(get_service_by_type(repository_class)),
        service=Depends(get_service_by_type(service_class))
    ):
        # Create in repository
        result = RouteHelper.create_entity(repository, entity.model_dump(), entity_type)
        
        # Initialize in service if applicable
        if hasattr(service, f'create_{entity_type.lower()}'):
            method = getattr(service, f'create_{entity_type.lower()}')
            method(entity.uid)
        
        return result
    return post_route

def create_put_route(repository_class, entity_type: str, model_class):
    """Create a standard put route."""
    async def put_route(
        entity: model_class,
        user: dict = Depends(require_authentication(f"update {entity_type.lower()}")),
        repository=Depends(get_service_by_type(repository_class))
    ):
        return RouteHelper.update_entity(repository, entity.model_dump(), entity_type)
    return put_route

def create_delete_route(repository_class, service_class, entity_type: str):
    """Create a standard delete route."""
    async def delete_route(
        entity_uid: str,
        user: dict = Depends(require_authentication(f"delete {entity_type.lower()}")),
        repository=Depends(get_service_by_type(repository_class)),
        service=Depends(get_service_by_type(service_class))
    ):
        # Delete from service if applicable
        if hasattr(service, f'delete_{entity_type.lower()}'):
            method = getattr(service, f'delete_{entity_type.lower()}')
            method(entity_uid)
        
        return RouteHelper.delete_entity(repository, entity_uid, entity_type)
    return delete_route