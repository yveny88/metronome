import os
from database.models import db, Song
from flask import Flask

# Chemin absolu pour garantir la création dans le dossier metronome
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'metronome.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if Song.query.count() == 0:
        songs = [
            Song(title="Sweet Home Alabama", bpm=100, beats_per_measure=4),
            Song(title="Sweet Child O' Mine", bpm=120, beats_per_measure=4),
            Song(title="Back in Black", bpm=140, beats_per_measure=4)
        ]
        db.session.bulk_save_objects(songs)
        db.session.commit()
        print("Base de données initialisée avec 3 chansons.")
    else:
        print("La base de données existe déjà et contient des chansons.")
