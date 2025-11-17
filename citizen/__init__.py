from flask import Blueprint

citizen_bp = Blueprint(
    "citizen_bp",
    __name__,
    template_folder="templates",
    static_folder="static"
)

from . import routes