"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""
from flask import request
from typing import List
from flask_jwt_extended import get_jwt_identity
from flask_login import current_user as session_user

from ...models import AppUser, Profile
from .basics import generate_random_string
from .loggers import console_log


def get_current_user() -> AppUser:
    if request.path.startswith('/api'):
        # API request, use JWT identity
        jwt_identity = get_jwt_identity()
    
        console_log("jwt_identity", jwt_identity)
    
        current_user_id = jwt_identity.get("user_id", 0)
        current_user: AppUser = AppUser.query.get(current_user_id)
    else:
        # Normal session request, use flask-login
        current_user = session_user
    
    return current_user


def get_app_user_info(user_id: int):
    """Gets profile details of a particular user"""
    
    if user_id is None:
        user_info: dict = {}
    else:
        app_user: AppUser = AppUser.query.filter(AppUser.id == user_id).first()
        user_info = app_user.to_dict()
    
    for key in user_info:
        if user_info[key] is None:
            user_info[key] = "—"
    
    return user_info


def is_user_exist(identifier, field, user=None):
    """
    Checks if a user exists in the database with the given identifier and field.

    Args:
        identifier: The identifier to search for (email or username).
        field: The field to search in ("email" or "username").
        user: An optional user object. If provided, the check excludes the user itself.

    Returns:
        True if the user exists, False otherwise.
    """
    base_query = AppUser.query.filter(getattr(AppUser, field) == identifier)
    if user:
        base_query = base_query.filter(AppUser.id != user.id)
    return base_query.scalar() is not None

def is_username_exist(username, user=None):
    """
    Checks if a username exists in the database, excluding the current user if provided.

    Args:
        username: The username to search for.
        user: An optional user object. If provided, the check excludes the user itself.

    Returns:
        True if the username is already taken, False if it's available.
    """
    base_query = AppUser.query.filter(AppUser.username == username)
    if user:
        # Query the database to check if the username is available, excluding the user's own username
        base_query = base_query.filter(AppUser.id != user.id)
    
    return base_query.scalar() is not None


def is_email_exist(email, user=None):
    """
    Checks if an email address exists in the database, excluding the current user if provided.

    Args:
        email: The email address to search for.
        user: An optional user object. If provided, the check excludes the user itself.

    Returns:
        True if the email address is already taken, False if it's available.
    """
    base_query = AppUser.query.filter(AppUser.email == email)
    if user:
        # Query the database to check if the email is available, excluding the user's own email
        base_query = base_query.filter(AppUser.id != user.id)
    
    return base_query.scalar() is not None


def get_app_user(email_username: str) -> AppUser:
    """
    Retrieves a AppUser object from the database based on email or username.

    Args:
        email_username: The email address or username to search for.

    Returns:
        The AppUser object if found, or None if not found.
    """
    
    user = AppUser.query.filter(AppUser.email == email_username).first()
    if user:
        return user
    
    return AppUser.query.filter(AppUser.username == email_username).first()


def generate_referral_code(length=6):
    while True:
        code = generate_random_string(length)
        # Check if the code already exists in the database
        if not referral_code_exists(code):
            return code

def referral_code_exists(code):
    profile = Profile.query.filter(Profile.referral_code == code).first()
    if profile:
        return True
    return False

