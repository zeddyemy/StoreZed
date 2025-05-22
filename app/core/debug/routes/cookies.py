"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""

from flask import (
    render_template, request, Response, make_response, flash, redirect, url_for, abort, session, current_app
)

from .. import debug_bp
from ....extensions import db
from ....utils.helpers.loggers import console_log
from ....utils.helpers.basics import redirect_url
from ....utils.decorators import web_admin_login_required

# this is to verify that cookies can be set
@debug_bp.route('/set-cookie')
def set_cookie():
    response = make_response('Cookie set')
    response.set_cookie('cookie name', 'cookie value')
    return response

@debug_bp.route('/get-cookie')
def get_cookie():
    if 'cookie name' in request.cookies:
        return 'Cookie found. Its value is %s.' % request.cookies['cookie name']
    else:
        return 'Cookie not found'

# this is to check if sessions work
@debug_bp.route('/set-session')
def set_session():
    session['session name'] = 'session value'
    return 'Session set'

@debug_bp.route('/get-session')
def get_session():
    if 'session name' in session:
        return 'Session value is %s.' % session['session name']
    else:
        return 'Session value not found'

@debug_bp.route('/test-session')
def test_session():
    session['test'] = 'works'
    return str(session.get('test'))