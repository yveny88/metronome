from flask import Blueprint, render_template
from src.database.models import Song

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    songs = Song.query.filter_by(prioritaire=1).all()
    return render_template('index.html', songs=songs)
