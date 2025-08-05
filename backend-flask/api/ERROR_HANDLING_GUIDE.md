# Centralized Error Handling System

This document describes the centralized error handling system implemented for the AOI (Automated Optical Inspection) backend API.

## Overview

The centralized error handling system eliminates duplicate error handling code across routes and ensures consistent error messages, status codes, and logging throughout the API.

## Key Components

### 1. Error Handlers (`api/error_handlers.py`)

**Functions:**
- `create_error_response()` - Creates standardized error responses
- `handle_route_errors()` - Decorator for automatic error handling
- `handle_cnc_operation_errors()` - Specialized CNC connection validation
- `validate_authentication()` - Authentication validation utility

**Error Mappings:**
- `UidNotFound` → 404 NOT FOUND
- `UidNotUnique` → 409 CONFLICT  
- `NoConfigurationChosen` → 400 BAD REQUEST
- `UserNotFound` → 404 NOT FOUND
- `NoLiveAlgSet` → 400 BAD REQUEST
- `NoLiveFrameSet` → 400 BAD REQUEST

### 2. Route Utilities (`api/route_utils.py`)

**RouteHelper Class:**
- `list_entities()` - Standardized entity listing
- `get_entity_by_id()` - Standardized entity retrieval  
- `create_entity()` - Standardized entity creation
- `update_entity()` - Standardized entity updates
- `delete_entity()` - Standardized entity deletion
- `create_success_response()` - Consistent success responses

**Dependencies:**
- `require_authentication()` - Authentication dependency
- Standard CRUD route factories

## Migration Guide

### Step 1: Add Imports

Add these imports to your route file:

```python
from api.error_handlers import create_error_response, validate_authentication
from api.route_utils import RouteHelper, require_authentication
```

### Step 2: Replace Authentication Checks

**Before:**
```python
@router.post("/")
async def create_item(
    item: ItemModel,
    user: dict = Depends(get_current_user),
    repository = Depends(get_service_by_type(Repository))
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed.")
    # ... rest of function
```

**After:**
```python
@router.post("/")
async def create_item(
    item: ItemModel,
    user: dict = Depends(require_authentication("create item")),
    repository = Depends(get_service_by_type(Repository))
):
    # ... rest of function (no manual auth check needed)
```

### Step 3: Replace CRUD Operations

**Before:**
```python
@router.get("/")
async def list_items(repository = Depends(get_service_by_type(Repository))):
    try:
        return repository.read_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list items: {e}")
```

**After:**  
```python
@router.get("/")
async def list_items(repository = Depends(get_service_by_type(Repository))):
    return RouteHelper.list_entities(repository, "Item")
```

**Before:**
```python
@router.get("/{item_uid}")
async def get_item(item_uid: str, repository = Depends(get_service_by_type(Repository))):
    try:
        item_data = repository.read_id(item_uid)
        return ItemModel(**item_data)
    except UidNotFound:
        raise HTTPException(status_code=404, detail=f"Item {item_uid} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get item: {e}")
```

**After:**
```python
@router.get("/{item_uid}")
async def get_item(item_uid: str, repository = Depends(get_service_by_type(Repository))):
    item_data = RouteHelper.get_entity_by_id(repository, item_uid, "Item") 
    return ItemModel(**item_data)
```

### Step 4: Replace Custom Error Handling

**Before:**
```python
try:
    result = some_complex_operation()
    return result
except SpecificException as e:
    raise HTTPException(status_code=400, detail=f"Operation failed: {e}")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
```

**After:**
```python
try:
    result = some_complex_operation()
    return result
except HTTPException:
    raise  # Re-raise HTTPExceptions
except Exception as e:
    raise create_error_response(
        operation="complex operation",
        entity_type="Item",
        entity_id=item_uid,
        exception=e
    )
```

### Step 5: CNC-Specific Operations

For CNC operations, use the specialized handler:

```python
@router.get("/{cnc_uid}/__API__/home")
async def home_cnc(
    cnc_uid: str,
    cnc_service: CncService = Depends(get_service_by_type(CncService))
):
    try:
        handle_cnc_operation_errors("home", cnc_service, cnc_uid)
        await cnc_service.home(cnc_uid)
        return RouteHelper.create_success_response(f"Home command executed on CNC {cnc_uid}")
    except HTTPException:
        raise
    except Exception as e:
        raise create_error_response(
            operation="execute home command",
            entity_type="CNC", 
            entity_id=cnc_uid,
            exception=e
        )
```

## Error Message Standards

### Consistent Naming
- Entity types: Use PascalCase (e.g., "CNC", "Configuration", "Camera")
- Operations: Use lowercase descriptive verbs (e.g., "create", "update", "delete", "execute home command")

### Error Response Format
All errors return this JSON structure:
```json
{
  "error": true,
  "message": "Descriptive error message",
  "status_code": 404,
  "path": "/api/endpoint"
}
```

### Success Response Format  
```json
{
  "status": "success",
  "message": "Operation completed successfully"
}
```

## Status Code Standards

| Exception Type | Status Code | Use Case |
|---|---|---|
| `UidNotFound` | 404 | Entity doesn't exist |
| `UidNotUnique` | 409 | Entity already exists |
| `Authentication Issues` | 401 | User not authenticated |
| `Authorization Issues` | 403 | User lacks permission |
| `Validation Errors` | 400 | Invalid request data |
| `Connection Issues` | 400 | Device/service unavailable |
| `General Errors` | 500 | Unexpected server errors |

## Logging

The error handling system automatically logs:
- All API errors with context
- Exception details for debugging
- Operation and entity information

Logs are written to the application's logging system and can be viewed in `app.log`.

## Migration Status

### ✅ Completed
- `cnc_routes.py` - Full migration with CNC-specific error handling
- `configuration_routes.py` - Full migration with configuration operations

### 🔄 Pending Migration
All other route files identified by the analysis script need migration:
- `robot_routes.py`
- `camera_routes.py`
- `authentication_routes.py`
- `algorithm_routes.py`
- And 17 others...

## Testing

After migrating a route file:

1. **Verify Imports**: Ensure all new imports resolve correctly
2. **Test Error Cases**: Verify error responses have consistent format
3. **Test Success Cases**: Ensure success responses work as expected
4. **Check Authentication**: Verify auth requirements work properly
5. **Review Logs**: Check that errors are logged appropriately

## Benefits

- **Consistency**: All API endpoints return errors in the same format
- **Maintainability**: Error handling logic is centralized
- **Debugging**: Better error messages with context
- **Security**: Consistent authentication handling
- **Performance**: Reduced code duplication
- **Standards**: Proper HTTP status codes throughout

## Example Migration

See `cnc_routes.py` for a complete example of the migrated error handling approach. This file demonstrates:

- Centralized imports
- Authentication dependencies  
- RouteHelper usage
- CNC-specific error handling
- Consistent success responses
- Proper exception handling patterns