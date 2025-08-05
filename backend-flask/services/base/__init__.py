"""
Base Services Package

Provides common base classes and mixins for all service implementations.
"""

from .base_service import BaseService, EntityManagerMixin, ConfigurableServiceMixin
from .repository_factory import (
    RepositoryFactory, 
    ServiceRepositoryMixin,
    create_standard_service_repositories,
    get_repository_for_service
)

__all__ = [
    'BaseService',
    'EntityManagerMixin', 
    'ConfigurableServiceMixin',
    'RepositoryFactory',
    'ServiceRepositoryMixin',
    'create_standard_service_repositories',
    'get_repository_for_service'
]

