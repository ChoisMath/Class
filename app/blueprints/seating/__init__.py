from flask import Blueprint

seating_bp = Blueprint('seating', __name__, url_prefix='/seating')

from . import routes