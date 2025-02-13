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
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app, request, redirect, flash, url_for, render_template
from flask_login import LoginManager, login_required, current_user as session_user

from app.models import AppUser
from ..helpers.http_response import error_response
from ..helpers.user import get_current_user

def roles_required(*required_roles):
    """
    Decorator to ensure that the current user has all of the specified roles.

    This decorator will return a 403 error if the current user does not have
    all of the roles specified in `required_roles`.

    Args:
        *required_roles (str): The required roles to access the route.

    Returns:
        function: The decorated function.

    Raises:
        HTTPException: A 403 error if the current user does not have the required roles.
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = get_current_user()
            
            if not current_user:
                return error_response("Unauthorized", 401)
            
            if current_user and any(user_role.role.name.value in required_roles for user_role in current_user.roles):
                return fn(*args, **kwargs)
            else:
                return error_response("Access denied: You do not have the required roles to access this resource", 403)
        return wrapper
    return decorator

def web_admin_login_required() -> None:
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


def session_roles_required(*required_roles):
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
                        return render_template('web_admin/errors/permission.html', msg="Access denied: You do not have the required roles to access this resource")
                    
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
