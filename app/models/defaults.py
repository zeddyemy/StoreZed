from flask import current_app
from slugify import slugify
from sqlalchemy import inspect

from ..extensions import db
from .user import AppUser, Profile, Address
from .wallet import Wallet
from .role import Role, UserRole
from .settings import GeneralSetting, PaymentMethodSettings
from ..utils.helpers.loggers import console_log

from ..enums.auth import RoleNames
from ..enums.settings import GeneralSettingsKeys, PaymentMethodSettingKeys


def create_default_super_admin(clear: bool = False) -> None:
    if inspect(db.engine).has_table('role'):
        admin_role = Role.query.filter_by(name=RoleNames.ADMIN).first()
        super_admin_role = Role.query.filter_by(name=RoleNames.SUPER_ADMIN).first()
        
        if not admin_role:
            admin_role = Role(
                name=RoleNames.ADMIN,
                slug=slugify(RoleNames.ADMIN.value)
            )
            db.session.add(admin_role)
            db.session.commit()
        
        if not super_admin_role:
            super_admin_role = Role(
                name=RoleNames.SUPER_ADMIN,
                slug=slugify(RoleNames.SUPER_ADMIN.value)
            )
            db.session.add(super_admin_role)
            db.session.commit()
    
    if inspect(db.engine).has_table('app_user'):
        admin = AppUser.query \
                .join(UserRole, AppUser.id == UserRole.app_user_id) \
                .join(Role, UserRole.role_id == Role.id) \
                .filter(Role.name == RoleNames.ADMIN).first()
        
        console_log("admin", admin)
        
        if clear and admin:
            # Clear existing roles before creating new ones
            admin.delete()
            db.session.close()
            console_log(data="Admin deleted successfully")
            return
        
        if not admin:
            admin_user = AppUser(
                username=current_app.config['DEFAULT_SUPER_ADMIN_USERNAME'],
                email='admin@admin.com'
            )
            admin_user.password=current_app.config['DEFAULT_SUPER_ADMIN_PASSWORD']
            
            admin_user_profile = Profile(firstname='admin', app_user=admin_user)
            admin_user_address = Address(app_user=admin_user)
            admin_user_wallet = Wallet(app_user=admin_user)
            
            db.session.add(admin_user)
            db.session.add_all([admin_user, admin_user_profile, admin_user_address, admin_user_wallet])
            db.session.commit()
            
            admin_user_role = UserRole.assign_role(admin_user, admin_role)
            super_admin_user_role = UserRole.assign_role(admin_user, super_admin_role)
            console_log(data="Admin user created with default credentials")
        else:
            console_log(data="Admin user already exists")


def create_roles(clear: bool = False) -> None:
    """Creates default roles if the "role" table doesn't exist.

    Args:
        clear (bool, optional): If True, clears all existing roles before creating new ones. Defaults to False.
    """
    if inspect(db.engine).has_table("role"):
        if clear:
            # Clear existing roles before creating new ones
            Role.query.delete()
            db.session.commit()
        
        for role_name in RoleNames:
            if not Role.query.filter_by(name=role_name).first():
                new_role = Role(name=role_name, slug=slugify(role_name.value))
                db.session.add(new_role)
        db.session.commit()


def initialize_settings():
    """
    Ensures all predefined settings keys exist in the database.
    If a key does not exist, it is initialized with its default value (or an empty string).
    """
    
    from ..utils.helpers.settings import get_default_setting
    if inspect(db.engine).has_table("general_setting"):
        # Iterate over all Enum members of GeneralSettingsKeys
        for key in GeneralSettingsKeys:
            existing_setting = GeneralSetting.query.filter_by(key=str(key)).first()
            if not existing_setting:
                setting = GeneralSetting(
                    key=str(key), 
                    value=get_default_setting(key)
                )
                db.session.add(setting)
        
        db.session.commit()


def initialize_payment_method_settings():
    """
    Ensures all predefined payment settings exist in the database.
    If a setting is missing, it is initialized with its default value.
    """
    from ..utils.helpers.settings import get_default_payment_method_settings
    default_payment_method_settings = get_default_payment_method_settings()
    if inspect(db.engine).has_table("payment_method_settings"):
        for method, settings in default_payment_method_settings.items():
            for key, default_value in settings.items():
                existing_setting = PaymentMethodSettings.query.filter_by(method=str(method), key=str(key)).first()
                if not existing_setting:
                    setting = PaymentMethodSettings(
                        method=str(method),
                        key=str(key),
                        value=default_value
                    )
                    db.session.add(setting)

        db.session.commit()
