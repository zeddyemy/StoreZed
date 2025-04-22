"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""

from slugify import slugify
from sqlalchemy import desc, inspect
from sqlalchemy.exc import DataError, DatabaseError
from werkzeug.security import generate_password_hash

from ...extensions import db
from ...enums.auth import RoleNames
from ...models.role import Role
from ...models.user import AppUser, Profile, Address
from .loggers import console_log, log_exception

def get_role_names(as_enum=False):
    """returns a list containing the names of all the roles"""
    role_names = []
    
    all_roles = db.session.query(Role.name).order_by(desc('id')).all()
    console_log('all_roles', all_roles)
    
    for role in all_roles:
        if as_enum:
            role_names.append(role.name)
        else:
            role_names.append(role.name.value)
    
    
    return role_names

def get_role_id(role_name):
    role_from_Db = Role.query.filter(Role.name.value == role_name).first()
    customer_role = Role.query.filter(Role.name.value == 'customer').first()
                    
    if role_from_Db:
        role_id = role_from_Db.id
    else:
        role_id = customer_role.id

    return role_id

def admin_roles():
    all_roles = Role.query.filter(Role.name != 'Customer').all()
    admin_roles = [role.name.value for role in all_roles]
    
    return admin_roles

def admin_editor_roles():
    all_roles = Role.query.filter(Role.name.in_(['Administrator', 'Editor'])).all()
    admin_editor_roles = [role.name for role in all_roles]
    
    return admin_editor_roles


def create_super_admin():
    try:
        super_admin_role = Role.query.filter_by(name=RoleNames.SUPER_ADMIN).first()
        
        if not super_admin_role:
            raise ValueError("No role found with the name SUPER_ADMIN")
        
        super_admins = super_admin_role.users.first()
        
        if not super_admins:
            super_admin = AppUser(username='admin', email='admin@mail.com', thePassword=generate_password_hash('root', "pbkdf2:sha256"))
            super_admin_profile = Profile(firstname='Admin', app_user=super_admin)
            super_admin_address = Address(app_user=super_admin)
        
            super_admin.roles.append(super_admin_role)
            
            db.session.add_all([super_admin, super_admin_profile, super_admin_address])
            db.session.commit()
    except (DataError, DatabaseError) as e:
        db.session.rollback()
        log_exception('Database error occurred during registration', e)
        raise e
    except Exception as e:
        db.session.rollback()
        log_exception('Error creating Admin User', e)
        raise e
    
def create_roles_and_super_admin(clear: bool = False) -> None:
    """Creates default roles if the 'role' table doesn't exist.

    Args:
        clear (bool, optional): If True, clears all existing roles before creating new ones. Defaults to False.
    """
    if inspect(db.engine).has_table('role'):
        if clear:
            # Clear existing roles before creating new ones
            Role.query.delete()
            db.session.commit()
        
        for role_name in RoleNames:
            if not Role.query.filter_by(name=role_name).first():
                new_role = Role(name=role_name, slug=slugify(role_name.value))
                db.session.add(new_role)
        db.session.commit()
        
        create_super_admin()


def normalize_role(role: str) -> str:
    """
    Normalize role name by converting to lowercase and removing extra spaces.
    
    Args:
        role (str): Role name to normalize
        
    Returns:
        str: Normalized role name
        
    Example:
        >>> normalize_role("Admin ")
        "admin"
        >>> normalize_role("SUPER ADMIN")
        "super admin"
    """
    return role.strip().lower()

