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
from flask import render_template, request, jsonify, redirect, url_for

@song_bp.route('/manage-songs', methods=['GET', 'POST'])
def manage_songs():
    if request.method == 'POST':
        title = request.form.get('title')
        bpm = request.form.get('bpm')
        min_speed = request.form.get('min_speed', 60)
        max_speed = request.form.get('max_speed', 120)
        challenge_speed = request.form.get('challenge_speed', 140)
        try:
            bpm = int(bpm)
            min_speed = int(min_speed)
            max_speed = int(max_speed)
            challenge_speed = int(challenge_speed)
            if not (40 <= bpm <= 240):
                return render_template('manage_songs.html', songs=Song.query.all(), message='Le BPM doit être entre 40 et 240', message_type='danger')
            new_song = Song(title=title, bpm=bpm, beats_per_measure=4, min_speed=min_speed, max_speed=max_speed, challenge_speed=challenge_speed)
            db.session.add(new_song)
            db.session.commit()
            message = f"La chanson '{title}' a été ajoutée avec succès !"
            mtype = 'success'
        except Exception as e:
            db.session.rollback()
            message = f"Erreur lors de l'ajout de la chanson : {str(e)}"
            mtype = 'danger'
        return render_template('manage_songs.html', songs=Song.query.all(), message=message, message_type=mtype)
    return render_template('manage_songs.html', songs=Song.query.all())

@song_bp.route('/delete-song/<int:song_id>')
def delete_song(song_id):
    try:
        song = Song.query.get_or_404(song_id)
        title = song.title
        db.session.delete(song)
        db.session.commit()
        message = f"La chanson '{title}' a été supprimée avec succès !"
        mtype = 'success'
    except Exception as e:
        db.session.rollback()
        message = f"Erreur lors de la suppression de la chanson : {str(e)}"
        mtype = 'danger'
    return render_template('manage_songs.html', songs=Song.query.all(), message=message, message_type=mtype)

@song_bp.route('/update-song-speeds/<int:song_id>', methods=['POST'])
def update_song_speeds(song_id):
    try:
        song = Song.query.get_or_404(song_id)
        data = request.get_json()
        song.min_speed = int(data['min_speed'])
        song.max_speed = int(data['max_speed'])
        song.challenge_speed = int(data['challenge_speed'])
        db.session.commit()
        return jsonify({'message': 'Vitesses mises à jour avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@song_bp.route('/update-song-prioritaire/<int:song_id>', methods=['POST'])
def update_song_prioritaire(song_id):
    try:
        song = Song.query.get_or_404(song_id)
        data = request.get_json()
        song.prioritaire = int(data['prioritaire'])
        db.session.commit()
        return jsonify({'message': 'Prioritaire mis à jour avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@song_bp.route('/update-songs-order-and-priority', methods=['POST'])
def update_songs_order_and_priority():
    try:
        data = request.get_json()
        normal = data.get('normal', [])
        priority = data.get('priority', [])
        for idx, song_id in enumerate(normal):
            song = Song.query.get(song_id)
            if song:
                song.prioritaire = 0
                song.display_order = idx
        for idx, song_id in enumerate(priority):
            song = Song.query.get(song_id)
            if song:
                song.prioritaire = 1
                song.display_order = idx
        db.session.commit()
        return jsonify({'message': 'Ordre et priorité mis à jour'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
