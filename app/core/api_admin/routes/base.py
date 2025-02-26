"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
"""

from .. import admin_api_bp

@admin_api_bp.route('/')
def index():
    return 'Admin API routes'