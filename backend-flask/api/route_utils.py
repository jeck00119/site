"""
Route Utilities

Common utilities and patterns for API routes to reduce code duplication.
"""

from typing import Any, Dict, List, Optional, Callable, Type
from fastapi import Depends, HTTPException, status
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from api.error_handlers import create_error_response, validate_authentication
from services.authorization.authorization import get_current_user
from services.configurations.configurations_service import ConfigurationService
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
    
    @staticmethod
    def setup_configuration_context(repository, configuration_service: ConfigurationService):
        """
        Apply configuration context to repository if current configuration exists.
        This centralizes the common pattern of setting database context.
        
        Args:
            repository: Repository instance to configure
            configuration_service: Configuration service instance
        """
        current_config = configuration_service.get_current_configuration_name()
        if current_config:
            repository.set_db(current_config)
    
    @staticmethod
    def get_entity_with_config_context(
        repository, 
        configuration_service: ConfigurationService,
        entity_uid: str, 
        entity_type: str = "Entity"
    ):
        """
        Get entity by ID with configuration context setup.
        Combines configuration setup and entity retrieval.
        """
        RouteHelper.setup_configuration_context(repository, configuration_service)
        return RouteHelper.get_entity_by_id(repository, entity_uid, entity_type)
    
    @staticmethod
    def list_entities_with_config_context(
        repository, 
        configuration_service: ConfigurationService,
        entity_type: str = "Entity"
    ) -> List[Dict]:
        """
        List entities with configuration context setup.
        Combines configuration setup and entity listing.
        """
        RouteHelper.setup_configuration_context(repository, configuration_service)
        return RouteHelper.list_entities(repository, entity_type)
    
    @staticmethod
    def create_entity_with_config_context(
        repository, 
        configuration_service: ConfigurationService,
        entity_data, 
        entity_type: str = "Entity"
    ):
        """
        Create entity with configuration context setup.
        Combines configuration setup and entity creation.
        """
        RouteHelper.setup_configuration_context(repository, configuration_service)
        return RouteHelper.create_entity(repository, entity_data, entity_type)
    
    @staticmethod
    def update_entity_with_config_context(
        repository, 
        configuration_service: ConfigurationService,
        entity_data, 
        entity_type: str = "Entity"
    ):
        """
        Update entity with configuration context setup.
        Combines configuration setup and entity update.
        """
        RouteHelper.setup_configuration_context(repository, configuration_service)
        return RouteHelper.update_entity(repository, entity_data, entity_type)
    
    @staticmethod
    def delete_entity_with_config_context(
        repository, 
        configuration_service: ConfigurationService,
        entity_uid: str, 
        entity_type: str = "Entity"
    ):
        """
        Delete entity with configuration context setup.
        Combines configuration setup and entity deletion.
        """
        RouteHelper.setup_configuration_context(repository, configuration_service)
        return RouteHelper.delete_entity(repository, entity_uid, entity_type)

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

def get_repository_with_config(repository_class: Type):
    """
    Create a dependency function that provides a repository with configuration context.
    
    Args:
        repository_class: Repository class to inject
        
    Returns:
        Dependency function that provides configured repository
    """
    async def _get_configured_repository(
        repository=Depends(get_service_by_type(repository_class)),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
    ):
        RouteHelper.setup_configuration_context(repository, configuration_service)
        return repository
    return _get_configured_repository

def get_repository_and_config_service(repository_class: Type):
    """
    Create a dependency function that provides both repository and configuration service.
    
    Args:
        repository_class: Repository class to inject
        
    Returns:
        Tuple of (repository, configuration_service)
    """
    async def _get_repo_and_config(
        repository=Depends(get_service_by_type(repository_class)),
        configuration_service: ConfigurationService = Depends(get_service_by_type(ConfigurationService))
    ):
        return repository, configuration_service
    return _get_repo_and_config

# Standard CRUD route factories
def create_list_route(repository_class, entity_type: str, with_config: bool = False):
    """Create a standard list route."""
    if with_config:
        async def list_route(
            repo_and_config=Depends(get_repository_and_config_service(repository_class))
        ):
            repository, configuration_service = repo_and_config
            return RouteHelper.list_entities_with_config_context(
                repository, configuration_service, entity_type
            )
    else:
        async def list_route(
            repository=Depends(get_service_by_type(repository_class))
        ):
            return RouteHelper.list_entities(repository, entity_type)
    return list_route

def create_get_route(repository_class, entity_type: str, model_class, with_config: bool = False):
    """Create a standard get by ID route."""
    if with_config:
        async def get_route(
            entity_uid: str,
            repo_and_config=Depends(get_repository_and_config_service(repository_class))
        ):
            repository, configuration_service = repo_and_config
            entity_data = RouteHelper.get_entity_with_config_context(
                repository, configuration_service, entity_uid, entity_type
            )
            return model_class(**entity_data)
    else:
        async def get_route(
            entity_uid: str,
            repository=Depends(get_service_by_type(repository_class))
        ):
            entity_data = RouteHelper.get_entity_by_id(repository, entity_uid, entity_type)
            return model_class(**entity_data)
    return get_route

def create_post_route(repository_class, service_class, entity_type: str, model_class, with_config: bool = False):
    """Create a standard post route."""
    if with_config:
        async def post_route(
            entity: model_class,
            user: dict = Depends(require_authentication(f"create {entity_type.lower()}")),
            repo_and_config=Depends(get_repository_and_config_service(repository_class)),
            service=Depends(get_service_by_type(service_class))
        ):
            repository, configuration_service = repo_and_config
            # Create in repository with config context
            result = RouteHelper.create_entity_with_config_context(
                repository, configuration_service, entity.model_dump(), entity_type
            )
            
            # Initialize in service if applicable
            if hasattr(service, f'create_{entity_type.lower()}'):
                method = getattr(service, f'create_{entity_type.lower()}')
                method(entity.uid)
            
            return result
    else:
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

def create_put_route(repository_class, entity_type: str, model_class, with_config: bool = False):
    """Create a standard put route."""
    if with_config:
        async def put_route(
            entity: model_class,
            user: dict = Depends(require_authentication(f"update {entity_type.lower()}")),
            repo_and_config=Depends(get_repository_and_config_service(repository_class))
        ):
            repository, configuration_service = repo_and_config
            return RouteHelper.update_entity_with_config_context(
                repository, configuration_service, entity.model_dump(), entity_type
            )
    else:
        async def put_route(
            entity: model_class,
            user: dict = Depends(require_authentication(f"update {entity_type.lower()}")),
            repository=Depends(get_service_by_type(repository_class))
        ):
            return RouteHelper.update_entity(repository, entity.model_dump(), entity_type)
    return put_route

def create_delete_route(repository_class, service_class, entity_type: str, with_config: bool = False):
    """Create a standard delete route."""
    if with_config:
        async def delete_route(
            entity_uid: str,
            user: dict = Depends(require_authentication(f"delete {entity_type.lower()}")),
            repo_and_config=Depends(get_repository_and_config_service(repository_class)),
            service=Depends(get_service_by_type(service_class))
        ):
            repository, configuration_service = repo_and_config
            # Delete from service if applicable
            if hasattr(service, f'delete_{entity_type.lower()}'):
                method = getattr(service, f'delete_{entity_type.lower()}')
                method(entity_uid)
            
            return RouteHelper.delete_entity_with_config_context(
                repository, configuration_service, entity_uid, entity_type
            )
    else:
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