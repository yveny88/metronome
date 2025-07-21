from flask import Flask
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import db, Song
from src.routes.song_routes import song_bp, init_db
from src.routes.main import main_bp
from src.routes.recordings import recordings_bp
from src.routes.goals import goals_bp
from src.routes.songsterr import songsterr_bp

app = Flask(__name__)
db_path = os.path.join('/app/data', 'metronome.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(main_bp)
app.register_blueprint(song_bp)
app.register_blueprint(recordings_bp)
app.register_blueprint(goals_bp)
app.register_blueprint(songsterr_bp)

with app.app_context():
    db.create_all()
    if Song.query.count() == 0:
        init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
