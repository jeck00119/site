"""
Base Router Module

Provides base classes and utilities to eliminate duplicate code in API routes.
Consolidates common CRUD patterns, error handling, and response formatting.
"""

from typing import Type, List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from starlette.responses import JSONResponse

from api.dependencies.services import get_service_by_type
from repo.repository_exceptions import UidNotFound, UidNotUnique
from services.authorization.authorization import get_current_user


class BaseRouter(ABC):
    """
    Abstract base class for API routers to eliminate duplicate patterns.
    
    Features:
    - Standardized CRUD operations
    - Consistent error handling
    - Common response formatting
    - Dependency injection patterns
    - Authentication integration
    """
    
    def __init__(self, 
                 prefix: str,
                 tags: List[str],
                 model_class: Type[BaseModel],
                 service_class: Type,
                 repository_class: Type):
        """
        Initialize base router.
        
        Args:
            prefix: URL prefix for routes
            tags: OpenAPI tags
            model_class: Pydantic model class
            service_class: Service class
            repository_class: Repository class
        """
        self.prefix = prefix
        self.tags = tags
        self.model_class = model_class
        self.service_class = service_class
        self.repository_class = repository_class
        
        # Create FastAPI router
        self.router = APIRouter(prefix=prefix, tags=tags)
        
        # Register standard routes
        self._register_routes()
    
    def _register_routes(self):
        """Register standard CRUD routes."""
        # List all entities
        @self.router.get("")
        async def list_entities(
            repository=Depends(get_service_by_type(self.repository_class))
        ):
            return await self._list_entities(repository)
        
        # Get single entity
        @self.router.get("/{entity_uid}")
        async def get_entity(
            entity_uid: str,
            repository=Depends(get_service_by_type(self.repository_class))
        ):
            return await self._get_entity(entity_uid, repository)
        
        # Create new entity
        @self.router.post("")
        async def create_entity(
            entity: self.model_class,
            service=Depends(get_service_by_type(self.service_class)),
            repository=Depends(get_service_by_type(self.repository_class)),
            current_user=Depends(get_current_user)
        ):
            return await self._create_entity(entity, service, repository)
        
        # Update entity
        @self.router.patch("/{entity_uid}")
        async def update_entity(
            entity_uid: str,
            entity: self.model_class,
            service=Depends(get_service_by_type(self.service_class)),
            repository=Depends(get_service_by_type(self.repository_class)),
            current_user=Depends(get_current_user)
        ):
            return await self._update_entity(entity_uid, entity, service, repository)
        
        # Delete entity
        @self.router.delete("/{entity_uid}")
        async def delete_entity(
            entity_uid: str,
            service=Depends(get_service_by_type(self.service_class)),
            repository=Depends(get_service_by_type(self.repository_class)),
            current_user=Depends(get_current_user)
        ):
            return await self._delete_entity(entity_uid, service, repository)
    
    async def _list_entities(self, repository) -> List[Dict[str, Any]]:
        """Default implementation for listing entities."""
        try:
            entities = repository.read_all()
            return [self._format_entity_summary(entity) for entity in entities]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list entities: {str(e)}"
            )
    
    async def _get_entity(self, entity_uid: str, repository) -> BaseModel:
        """Default implementation for getting single entity."""
        try:
            entity_data = repository.read_id(entity_uid)
            return self.model_class(**entity_data)
        except UidNotFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with UID {entity_uid} not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get entity: {str(e)}"
            )
    
    async def _create_entity(self, entity: BaseModel, service, repository) -> JSONResponse:
        """Default implementation for creating entity."""
        try:
            # Save to repository
            repository.create(entity.model_dump())
            
            # Initialize in service if applicable
            if hasattr(service, 'post_entity'):
                result = service.post_entity(entity)
            elif hasattr(service, f'post_{self._get_entity_name()}'):
                method = getattr(service, f'post_{self._get_entity_name()}')
                result = method(entity)
            
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "status": "success",
                    "message": f"Entity {entity.uid} created successfully",
                    "uid": entity.uid
                }
            )
        except UidNotUnique:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Entity with UID {entity.uid} already exists"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create entity: {str(e)}"
            )
    
    async def _update_entity(self, entity_uid: str, entity: BaseModel, service, repository) -> JSONResponse:
        """Default implementation for updating entity."""
        try:
            # Ensure UID matches
            entity.uid = entity_uid
            
            # Update in repository
            repository.update(entity.model_dump())
            
            # Update in service if applicable
            if hasattr(service, 'patch_entity'):
                result = service.patch_entity(entity)
            elif hasattr(service, f'patch_{self._get_entity_name()}'):
                method = getattr(service, f'patch_{self._get_entity_name()}')
                result = method(entity)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "success",
                    "message": f"Entity {entity_uid} updated successfully",
                    "uid": entity_uid
                }
            )
        except UidNotFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with UID {entity_uid} not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update entity: {str(e)}"
            )
    
    async def _delete_entity(self, entity_uid: str, service, repository) -> JSONResponse:
        """Default implementation for deleting entity."""
        try:
            # Delete from service if applicable
            if hasattr(service, 'delete_entity'):
                result = service.delete_entity(entity_uid)
            elif hasattr(service, f'delete_{self._get_entity_name()}'):
                method = getattr(service, f'delete_{self._get_entity_name()}')
                result = method(entity_uid)
            
            # Delete from repository
            repository.delete(entity_uid)
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "success",
                    "message": f"Entity {entity_uid} deleted successfully",
                    "uid": entity_uid
                }
            )
        except UidNotFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entity with UID {entity_uid} not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete entity: {str(e)}"
            )
    
    def _format_entity_summary(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Format entity for summary listing. Override in subclasses."""
        return {
            'uid': entity.get('uid'),
            'name': entity.get('name', 'Unknown')
        }
    
    def _get_entity_name(self) -> str:
        """Get entity name from model class. Override if needed."""
        return self.model_class.__name__.lower().replace('model', '')
    
    def add_custom_route(self, path: str, methods: List[str], handler: Callable):
        """Add custom route to the router."""
        for method in methods:
            if method.upper() == 'GET':
                self.router.get(path)(handler)
            elif method.upper() == 'POST':
                self.router.post(path)(handler)
            elif method.upper() == 'PUT':
                self.router.put(path)(handler)
            elif method.upper() == 'PATCH':
                self.router.patch(path)(handler)
            elif method.upper() == 'DELETE':
                self.router.delete(path)(handler)


class CRUDRouter(BaseRouter):
    """
    Specialized router for simple CRUD operations.
    
    Provides all standard CRUD endpoints with minimal configuration.
    """
    
    def __init__(self, 
                 prefix: str,
                 tags: List[str],
                 model_class: Type[BaseModel],
                 service_class: Type,
                 repository_class: Type,
                 entity_name: str = None):
        """
        Initialize CRUD router.
        
        Args:
            prefix: URL prefix
            tags: OpenAPI tags
            model_class: Pydantic model
            service_class: Service class
            repository_class: Repository class
            entity_name: Custom entity name (optional)
        """
        self.entity_name = entity_name
        super().__init__(prefix, tags, model_class, service_class, repository_class)
    
    def _get_entity_name(self) -> str:
        """Get entity name."""
        if self.entity_name:
            return self.entity_name
        return super()._get_entity_name()


class ProcessingRouter(BaseRouter):
    """
    Specialized router for entities that support processing operations.
    
    Adds processing endpoints in addition to standard CRUD.
    """
    
    def _register_routes(self):
        """Register routes including processing endpoints."""
        super()._register_routes()
        
        # Add processing endpoint
        @self.router.post("/{entity_uid}/process")
        async def process_entity(
            entity_uid: str,
            service=Depends(get_service_by_type(self.service_class)),
            current_user=Depends(get_current_user)
        ):
            return await self._process_entity(entity_uid, service)
    
    async def _process_entity(self, entity_uid: str, service) -> JSONResponse:
        """Default implementation for processing entity."""
        try:
            if hasattr(service, 'process_entity'):
                result = service.process_entity(entity_uid)
            elif hasattr(service, f'process_{self._get_entity_name()}'):
                method = getattr(service, f'process_{self._get_entity_name()}')
                result = method(entity_uid)
            else:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail=f"Processing not implemented for {self._get_entity_name()}"
                )
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "success",
                    "message": f"Entity {entity_uid} processed successfully",
                    "result": result
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process entity: {str(e)}"
            )


class StatusRouter(BaseRouter):
    """
    Specialized router for entities that support status operations.
    
    Adds status endpoints in addition to standard CRUD.
    """
    
    def _register_routes(self):
        """Register routes including status endpoints."""
        super()._register_routes()
        
        # Add status endpoint
        @self.router.get("/{entity_uid}/status")
        async def get_entity_status(
            entity_uid: str,
            service=Depends(get_service_by_type(self.service_class))
        ):
            return await self._get_entity_status(entity_uid, service)
        
        # Add bulk status endpoint
        @self.router.get("/status/all")
        async def get_all_entities_status(
            service=Depends(get_service_by_type(self.service_class))
        ):
            return await self._get_all_entities_status(service)
    
    async def _get_entity_status(self, entity_uid: str, service) -> JSONResponse:
        """Get status for single entity."""
        try:
            if hasattr(service, 'get_entity_status'):
                result = service.get_entity_status(entity_uid)
            elif hasattr(service, f'get_{self._get_entity_name()}_status'):
                method = getattr(service, f'get_{self._get_entity_name()}_status')
                result = method(entity_uid)
            else:
                result = {"status": "unknown", "message": "Status not available"}
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=result
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get entity status: {str(e)}"
            )
    
    async def _get_all_entities_status(self, service) -> JSONResponse:
        """Get status for all entities."""
        try:
            if hasattr(service, 'get_all_entities_status'):
                result = service.get_all_entities_status()
            elif hasattr(service, f'get_all_{self._get_entity_name()}s_status'):
                method = getattr(service, f'get_all_{self._get_entity_name()}s_status')
                result = method()
            else:
                result = {"status": "unknown", "message": "Bulk status not available"}
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=result
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get all entities status: {str(e)}"
            )


# Utility functions for common route patterns
def create_standard_crud_router(
    prefix: str,
    tags: List[str],
    model_class: Type[BaseModel],
    service_class: Type,
    repository_class: Type,
    entity_name: str = None
) -> APIRouter:
    """
    Create a standard CRUD router with minimal configuration.
    
    Args:
        prefix: URL prefix
        tags: OpenAPI tags
        model_class: Pydantic model
        service_class: Service class
        repository_class: Repository class
        entity_name: Custom entity name
        
    Returns:
        Configured APIRouter
    """
    crud_router = CRUDRouter(prefix, tags, model_class, service_class, repository_class, entity_name)
    return crud_router.router


def create_processing_router(
    prefix: str,
    tags: List[str],
    model_class: Type[BaseModel],
    service_class: Type,
    repository_class: Type,
    entity_name: str = None
) -> APIRouter:
    """
    Create a processing router with CRUD + processing endpoints.
    
    Args:
        prefix: URL prefix
        tags: OpenAPI tags
        model_class: Pydantic model
        service_class: Service class
        repository_class: Repository class
        entity_name: Custom entity name
        
    Returns:
        Configured APIRouter
    """
    processing_router = ProcessingRouter(prefix, tags, model_class, service_class, repository_class)
    if entity_name:
        processing_router.entity_name = entity_name
    return processing_router.router


def create_status_router(
    prefix: str,
    tags: List[str],
    model_class: Type[BaseModel],
    service_class: Type,
    repository_class: Type,
    entity_name: str = None
) -> APIRouter:
    """
    Create a status router with CRUD + status endpoints.
    
    Args:
        prefix: URL prefix
        tags: OpenAPI tags
        model_class: Pydantic model
        service_class: Service class
        repository_class: Repository class
        entity_name: Custom entity name
        
    Returns:
        Configured APIRouter
    """
    status_router = StatusRouter(prefix, tags, model_class, service_class, repository_class)
    if entity_name:
        status_router.entity_name = entity_name
    return status_router.router

