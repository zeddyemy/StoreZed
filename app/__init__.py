from flask import Flask


from config import Config, config_by_name, configure_logging
from .context_processors import app_context_Processor
from .extensions import initialize_extensions, login_manager
from .models import AppUser, create_db_defaults
from .utils.date_time import timezone
from .utils.hooks import register_hooks
from .utils.helpers.loggers import console_log


def create_app(config_name=Config.ENV, create_defaults=True):
    '''
    Creates and configures the Flask application instance.

    Args:
        config_name: The configuration class to use (Defaults to Config).

    Returns:
        The Flask application instance.
    '''
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.context_processor(app_context_Processor)
    
    # Initialize Flask extensions
    initialize_extensions(app=app)
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return AppUser.query.get(int(user_id))
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
    
    # create defaults
    if create_defaults:
        create_db_defaults(app)
    
    return app