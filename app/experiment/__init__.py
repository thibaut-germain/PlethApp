from flask import Blueprint

bp = Blueprint('experiment', __name__)

from app.experiment import routes