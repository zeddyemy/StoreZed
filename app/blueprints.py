"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
"""

from flask import Flask, Blueprint

def register_all_blueprints(app: Flask) -> None:
    
    from .core.web_front import web_front_bp
    app.register_blueprint(web_front_bp)
    
    from .core.web_admin import web_admin_bp
    app.register_blueprint(web_admin_bp)
    
    from .core.api import api_bp
    app.register_blueprint(api_bp)
    
    from .core.api_admin import admin_api_bp
    app.register_blueprint(admin_api_bp)
    
    
    # Swagger setup
    from flask_swagger_ui import get_swaggerui_blueprint

    SWAGGER_URL: str = '/swagger'
    API_URL: str = '/static/swagger.json'
    swaggerui_blueprint: Blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
