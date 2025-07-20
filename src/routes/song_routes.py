from flask import Blueprint, request, jsonify
from src.database.models import db, Song

song_bp = Blueprint('songs', __name__)

def init_db():
    # Vérifier si la base de données est vide
    if Song.query.count() == 0:
        # Ajouter 3 chansons
        songs = [
            Song(title="Sweet Home Alabama", bpm=100, beats_per_measure=4),
            Song(title="Sweet Child O' Mine", bpm=120, beats_per_measure=4),
            Song(title="Back in Black", bpm=140, beats_per_measure=4)
        ]
        for song in songs:
            db.session.add(song)
        db.session.commit()

@song_bp.route("/add_song", methods=['POST'])
def add_song():
    data = request.get_json()
    new_song = Song(
        title=data['title'],
        bpm=data['bpm'],
        beats_per_measure=data['beats_per_measure']
    )
    db.session.add(new_song)
    db.session.commit()
    return jsonify({"message": "Chanson ajoutée avec succès"})

@song_bp.route("/get_songs", methods=['GET'])
def get_songs():
    songs = Song.query.all()
    return jsonify([song.to_dict() for song in songs])
