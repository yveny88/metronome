from flask import Blueprint, render_template
from src.database.models import Song

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('metronome.html')
