import os
from database.models import db, Song
from flask import Flask

# Chemin absolu pour la base de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'metronome.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    print("\nContenu de la base de données :")
    print("-" * 50)
    songs = Song.query.all()
    if songs:
        print(f"Nombre de chansons : {len(songs)}")
        print("\nListe des chansons :")
        print("-" * 50)
        for song in songs:
            print(f"Titre : {song.title}")
            print(f"BPM : {song.bpm}")
            print(f"Temps : {song.beats_per_measure}/4")
            print("-" * 50)
    else:
        print("La base de données est vide.")
