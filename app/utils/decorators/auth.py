'''
This module defines the `roles_required` decorator for the Flask application.

Used for handling role-based access control.
The `roles_required` decorator is used to ensure that the current user has all of the specified roles.
If the user does not have the required roles, it returns a 403 error.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
Package: BitnShop
'''
from functools import wraps
from typing import Callable, TypeVar, Tuple, Any, Union
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app,  request, redirect, flash, url_for, render_template, Response
from flask.typing import ResponseReturnValue
from flask_login import LoginManager, login_required, current_user as session_user

from app.models import AppUser
from ..helpers.loggers import console_log
from ..helpers.http_response import error_response
from ..helpers.user import get_current_user
from ..helpers.roles import normalize_role

# Define type variables for better type hinting
F = TypeVar('F', bound=Callable[..., Any])

def web_admin_login_required():
    """
    Decorator to ensure that the user is authenticated for accessing admin routes.
    If the user is not authenticated, they are redirected to the admin login page.

    Returns:
        function: The decorated function.

    Raises:
        redirect: Redirects to the admin login page if the user is not authenticated.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            next=request.path
            if not session_user.is_authenticated:
                flash("You need to login first", 'error')
                return redirect(url_for('web_admin.login', next=next))

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def session_roles_required(*required_roles: str) -> Callable[[F], F]:
    """
    Decorator to restrict access to session-based routes based on user roles. 
    The current user must have the roles specified in `required_roles`.

    Args:
        *required_roles (str): The required roles to access the route.

    Returns:
        function: The decorated function.
    
    Raises:
        redirect: Redirects to a login page or a permission denied page if the user does not have the required roles.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.blueprint == 'web_admin':
                # Admin route
                @web_admin_login_required()
                def inner_wrapper(*args, **kwargs):
                    current_user = get_current_user()
                    # Check if user has the required roles
                    if not any(user_role.role.name.value in required_roles for user_role in current_user.roles):
                        return render_template('web_admin/errors/misc/permission.html', msg="Access denied: You do not have the required roles to access this resource")
                    
                    return fn(*args, **kwargs)
                
                return inner_wrapper(*args, **kwargs)
            else:
                # Frontend route
                @login_required()
                def inner_wrapper(*args, **kwargs):
                    current_user = session_user
                    # Check if user has the required roles
                    if not any(user_role.role.name.value in required_roles for user_role in current_user.roles):
                        return render_template('web_front/errors/permission.html', msg="Access denied: You do not have the required roles to access this resource")
                    
                    return fn(*args, **kwargs)
                
                return inner_wrapper(*args, **kwargs)
        
        return wrapper
    
    return decorator


def roles_required(*required_roles: str) -> Callable[[F], F]:
    """
    Smart decorator that handles both JWT and session-based authentication with role verification.
    
    It ensures that the current user has one of the specified roles.
    
    This decorator provides a unified authentication and authorization mechanism that works for:
    1. API requests with JWT authentication
    2. AJAX requests from web interface
    3. Regular web requests with session-based authentication

    Authentication Flow:
    - For API/AJAX requests:
        1. Attempts JWT authentication first
        2. Falls back to session authentication if JWT fails/not present
        3. Returns JSON responses for success/failure
    
    - For web requests:
        1. Uses Flask-Login session authentication
        2. Handles redirects to appropriate login pages
        3. Renders error templates for permission issues

    Args:
        *required_roles (str): Variable length argument of role names that are required to access the decorated route.
    
    Returns:
        Callable: Decorated function that enforces authentication and role checks
    
    Response Types:
        - API/AJAX requests:
            - 401 Unauthorized: When authentication fails
            - 403 Forbidden: When role check fails
            - JSON responses with appropriate messages
        
        - Web requests:
            - Redirect to login page: When not authenticated
            - Error template: When role check fails
            - Original response: When all checks pass

    """
    
    # Normalize required roles once at decoration time
    normalized_required_roles = {normalize_role(role) for role in required_roles}
    
    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Union[ResponseReturnValue, Response]:
            is_api_request: bool = (
                request.path.startswith('/api') or 
                request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            )

            # Handle API/AJAX requests
            if is_api_request:
                # API/AJAX request - use JWT if token present, fallback to session
                try:
                    jwt_required()(lambda: None)()  # Verify JWT if present
                    current_user: AppUser = get_current_user()  # Will use JWT identity
                except:
                    # Fallback to session user if JWT fails/not present
                    current_user = session_user
                
                if not current_user or not current_user.is_authenticated:
                    return error_response("Unauthorized", 401)
                
                # Check roles for API requests
                if not any(normalize_role(user_role.role.name.value) in normalized_required_roles 
                        for user_role in current_user.roles):
                    return error_response(
                        "Access denied: Insufficient permissions", 
                        403
                    )
            
            # Handle web requests - use session authentication
            else:
                if not session_user.is_authenticated:
                    next_url: str = request.path
                    flash("You need to login first", 'error')
                    if request.blueprint == 'web_admin':
                        return redirect(url_for('web_admin.login', next=next_url))
                    return redirect(url_for('web_front.login', next=next_url))
                
                # Check roles for web requests
                if not any(normalize_role(user_role.role.name.value) in normalized_required_roles 
                        for user_role in session_user.roles):
                    template: str = (
                        'web_admin/errors/misc/permission.html' 
                        if request.blueprint == 'web_admin'
                        else 'web_front/errors/permission.html'
                    )
                    return render_template(
                        template,
                        msg="Access denied: You do not have the required roles to access this resource"
                    )
            
            return fn(*args, **kwargs)
        return wrapper  # type: ignore
    return decorator