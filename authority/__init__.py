from flask import Blueprint

authority_bp = Blueprint(
    'authority_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)


# Import routes AFTER models are loaded
from . import routes
