from flask import Blueprint

bp = Blueprint('load_data', __name__)

from app.load_data import routes