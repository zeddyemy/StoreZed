from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from config import Config, config_by_name, configure_logging
from .context_processors import app_context_Processor
from .extensions import initialize_extensions, login_manager
from .models import AppUser, UserRole, create_db_defaults
from .utils.date_time import timezone
from .utils.hooks import register_hooks
from .utils.helpers.loggers import console_log
from .extensions import db


def create_app(config_name=Config.ENV, create_defaults=True):
    '''
    Creates and configures the Flask application instance.

    Args:
        config_name: The configuration class to use (Defaults to Config).

    Returns:
        The Flask application instance.
    '''
    app = Flask(__name__)
    
    # --> Add ProxyFix BEFORE loading config <--
    # Tell it Render likely sets X-Forwarded-Proto (1 proxy hop)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    # --> End ProxyFix <--
    
    app.config.from_object(config_by_name[config_name])
    app.context_processor(app_context_Processor)
    
    # Initialize Flask extensions
    initialize_extensions(app=app)
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            stmt = select(AppUser).options(joinedload(AppUser.roles)).filter_by(id=int(user_id))
            return db.session.execute(stmt).scalar_one_or_none()
        except Exception as e:
            app.logger.error(f"Error loading user {user_id}: {e}")
            return None
    
    
    # Register before and after request hooks
    register_hooks(app=app)
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    from .blueprints import register_all_blueprints
    register_all_blueprints(app)
    
    # initialize database defaults values
    if create_defaults:
        create_db_defaults(app)
    
    return app