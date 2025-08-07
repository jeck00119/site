#!/usr/bin/env python3
"""
Script to apply centralized error handling to all route files.

This script helps identify and update routes that need to be migrated
to use the centralized error handling system.
"""

import os
import re
from pathlib import Path

# Configuration
ROUTES_DIR = Path("api/routers")
ROUTE_FILES = [
    "robot_routes.py",
    "camera_routes.py", 
    "authentication_routes.py",
    "algorithm_routes.py",
    "components_routes.py",
    "locations_routes.py",
    "media_routes.py",
    "profilometer_routes.py",
    "references_routes.py",
    "identifications_routes.py",
    "itac_routes.py",
    "custom_components_routes.py",
    "process_routes.py",
    "camera_settings_routes.py",
    "camera_calibration_routes.py",
    "stereo_callibration_routes.py",
    "annotation_routes.py",
    "image_generator_routes.py",
    "image_source_routes.py",
    "peripheral_routes.py",
    "inspection_list_routes.py"
]

def analyze_route_file(file_path: Path) -> dict:
    """Analyze a route file and identify error handling patterns."""
    
    if not file_path.exists():
        return {"error": "File not found", "issues": []}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": f"Could not read file: {e}", "issues": []}
    
    issues = []
    
    # Check for inconsistent status code usage
    uid_not_found_400 = re.findall(r'UidNotFound.*status_code=400', content)
    uid_not_found_404 = re.findall(r'UidNotFound.*status_code=404', content)
    
    if uid_not_found_400 and uid_not_found_404:
        issues.append("Inconsistent UidNotFound status codes (both 400 and 404 used)")
    
    # Check for raw status codes instead of constants
    raw_status_codes = re.findall(r'status_code=\d+', content)
    if raw_status_codes:
        issues.append(f"Raw status codes found: {set(raw_status_codes)}")
    
    # Check for authentication patterns
    auth_checks = re.findall(r'if user is None:', content)
    if auth_checks:
        issues.append(f"Manual authentication checks found: {len(auth_checks)} instances")
    
    # Check for missing error handling
    routes_without_try = []
    route_functions = re.findall(r'@router\.(get|post|put|delete|patch)\([^)]+\)\s*async def (\w+)', content)
    
    for method, func_name in route_functions:
        func_pattern = rf'async def {func_name}.*?(?=async def|\Z)'
        func_match = re.search(func_pattern, content, re.DOTALL)
        if func_match and 'try:' not in func_match.group(0):
            routes_without_try.append(f"{method.upper()} {func_name}")
    
    if routes_without_try:
        issues.append(f"Routes without try-catch blocks: {routes_without_try}")
    
    # Check for missing imports
    missing_imports = []
    if 'HTTPException' in content and 'from fastapi import' in content:
        fastapi_import = re.search(r'from fastapi import ([^\n]+)', content)
        if fastapi_import and 'HTTPException' not in fastapi_import.group(1):
            missing_imports.append("HTTPException not in fastapi import")
    
    if 'status.' in content and 'from starlette import status' not in content:
        missing_imports.append("status constants used but not imported")
    
    if missing_imports:
        issues.append(f"Import issues: {missing_imports}")
    
    # Count different error patterns
    error_patterns = {
        'HTTPException': len(re.findall(r'HTTPException\(', content)),
        'try_catch_blocks': len(re.findall(r'try:', content)),
        'f_string_errors': len(re.findall(r"detail=f['\"]", content)),
        'raise_statements': len(re.findall(r'raise HTTPException', content))
    }
    
    return {
        "issues": issues,
        "error_patterns": error_patterns,
        "needs_migration": len(issues) > 0,
        "file_size": len(content.splitlines())
    }

def generate_migration_plan():
    """Generate a migration plan for all route files."""
    
    print("Analyzing route files for error handling patterns...\n")
    
    results = {}
    total_issues = 0
    
    for route_file in ROUTE_FILES:
        file_path = ROUTES_DIR / route_file
        print(f"Analyzing {route_file}...")
        
        result = analyze_route_file(file_path)
        results[route_file] = result
        
        if result.get("error"):
            print(f"  ERROR: {result['error']}")
            continue
        
        issues = result.get("issues", [])
        if issues:
            print(f"  WARNING: {len(issues)} issues found:")
            for issue in issues:
                print(f"    - {issue}")
            total_issues += len(issues)
        else:
            print(f"  OK: No issues found")
        
        patterns = result.get("error_patterns", {})
        if patterns:
            print(f"  Patterns: {patterns}")
        
        print()
    
    # Summary
    print("="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    
    needs_migration = [f for f, r in results.items() if r.get("needs_migration", False)]
    
    print(f"Total files analyzed: {len(ROUTE_FILES)}")
    print(f"Files needing migration: {len(needs_migration)}")
    print(f"Total issues found: {total_issues}")
    
    if needs_migration:
        print("\nFiles requiring migration:")
        for file_name in needs_migration:
            print(f"  - {file_name}")
    
    print("\nRecommended migration steps:")
    print("  1. Add centralized error handling imports")
    print("  2. Replace manual authentication checks with require_authentication() dependency")
    print("  3. Replace try-catch blocks with RouteHelper methods")
    print("  4. Standardize status codes (UidNotFound -> 404, UidNotUnique -> 409)")
    print("  5. Use create_error_response() for consistent error messages")
    
    return results

def generate_import_template():
    """Generate the standard import template for routes."""
    
    template = '''# Add these imports for centralized error handling:
from api.error_handlers import create_error_response, validate_authentication
from api.route_utils import RouteHelper, require_authentication

# Replace manual authentication checks with:
# user: dict = Depends(require_authentication("operation description"))

# Replace try-catch blocks with RouteHelper methods:
# RouteHelper.list_entities(repository, "EntityType")
# RouteHelper.get_entity_by_id(repository, entity_uid, "EntityType")
# RouteHelper.create_entity(repository, entity_data, "EntityType")
# RouteHelper.update_entity(repository, entity_data, "EntityType")
# RouteHelper.delete_entity(repository, entity_uid, "EntityType")

# Use create_error_response() for custom errors:
# raise create_error_response(
#     operation="action_name",
#     entity_type="EntityType",
#     entity_id=entity_uid,
#     exception=e
# )
'''
    
    print("IMPORT TEMPLATE FOR ROUTE MIGRATION")
    print("="*50)
    print(template)

if __name__ == "__main__":
    print("AOI Error Handling Migration Tool")
    print("="*50)
    
    # Check if we're in the right directory
    if not ROUTES_DIR.exists():
        print(f"Routes directory not found: {ROUTES_DIR}")
        print("   Make sure you're running this from the backend-flask directory")
        exit(1)
    
    # Generate migration plan
    results = generate_migration_plan()
    
    # Show import template
    generate_import_template()
    
    print("\nAnalysis complete!")
    print("\nNext steps:")
    print("   1. Review the issues identified above")
    print("   2. Use the import template to update route files")
    print("   3. Test each migrated route file")
    print("   4. Update documentation as needed")