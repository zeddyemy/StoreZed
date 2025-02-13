"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

from flask import Flask

def register_all_blueprints(app: Flask) -> None:
    
    from .core.web_front.routes import web_front_bp
    app.register_blueprint(web_front_bp)
    
    from .core.web_admin.routes import web_admin_bp
    app.register_blueprint(web_admin_bp)
    
    from .core.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    from .core.api_admin.routes import admin_api_bp
    app.register_blueprint(admin_api_bp)
    
    
    # Swagger setup
    from flask_swagger_ui import get_swaggerui_blueprint

    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
