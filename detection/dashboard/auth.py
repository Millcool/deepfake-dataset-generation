"""
Flask-Login setup: login_manager, load_user callback, admin_required decorator.
"""

from functools import wraps

from flask import redirect, url_for, flash, abort
from flask_login import LoginManager, current_user

from models import User

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Необходимо войти в систему."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator: require current_user.role == 'admin'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated
