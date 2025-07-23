from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import os
import sys
import subprocess
from werkzeug.utils import secure_filename

# Ajouter le répertoire src au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import db, Song, GuitarGoal, SongsterrLink
from src.routes.song_routes import song_bp, init_db

app = Flask(__name__)
# Utiliser un chemin dans le volume Docker pour la base de données
db_path = os.path.join('/app/data', 'metronome.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser la base de données
db.init_app(app)

# Enregistrer les blueprints
app.register_blueprint(song_bp)

# Créer les tables de la base de données et initialiser avec des données
# seulement si la base n'existe pas ou est vide
with app.app_context():
    # Créer les tables si elles n'existent pas
    db.create_all()
    
    # Initialiser avec des données seulement si la base est vide
    if Song.query.count() == 0:
        init_db()

@app.route("/")
def index():
    with app.app_context():
        songs = Song.query.filter_by(prioritaire=1).all()
    return render_template("index.html", songs=songs)

@app.route("/recordings")
def recordings_page():
    recordings_dir = '/app/data'
    try:
        files = [f for f in os.listdir(recordings_dir) if f.lower().endswith(('.webm', '.wav', '.mp3'))]
    except FileNotFoundError:
        files = []
    return render_template("recordings.html", recordings=files, message=None, message_type=None)

@app.route('/data/<path:filename>')
def data_file(filename):
    return send_from_directory('/app/data', filename)

@app.route('/delete-recording/<path:filename>')
def delete_recording(filename):
    recordings_dir = '/app/data'
    safe_name = secure_filename(filename)
    file_path = os.path.join(recordings_dir, safe_name)
    message = ""
    message_type = ""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            message = "Enregistrement supprimé."
            message_type = "success"
    except Exception as e:
        message = f"Erreur lors de la suppression : {str(e)}"
        message_type = "error"
    files = [f for f in os.listdir(recordings_dir) if f.lower().endswith(('.webm', '.wav', '.mp3'))]
    return render_template("recordings.html", recordings=files, message=message, message_type=message_type)

@app.route("/manage-songs", methods=['GET', 'POST'])
def manage_songs():
    with app.app_context():
        if request.method == 'POST':
            title = request.form.get('title')
            bpm = request.form.get('bpm')
            min_speed = request.form.get('min_speed', 60)
            max_speed = request.form.get('max_speed', 120)
            challenge_speed = request.form.get('challenge_speed', 140)
            intermediate_measures = request.form.get('intermediate_measures', 1)
            
            try:
                bpm = int(bpm)
                min_speed = int(min_speed)
                max_speed = int(max_speed)
                challenge_speed = int(challenge_speed)
                intermediate_measures = int(intermediate_measures)
                
                if not (40 <= bpm <= 240):
                    return render_template(
                        "manage_songs.html",
                        songs=Song.query.all(),
                        message="Le BPM doit être entre 40 et 240",
                        message_type="error"
                    )
                
                new_song = Song(
                    title=title,
                    bpm=bpm,
                    beats_per_measure=4,
                    intermediate_measures=intermediate_measures,
                    min_speed=min_speed,
                    max_speed=max_speed,
                    challenge_speed=challenge_speed
                )
                db.session.add(new_song)
                db.session.commit()
                
                return render_template(
                    "manage_songs.html",
                    songs=Song.query.all(),
                    message=f"La chanson '{title}' a été ajoutée avec succès !",
                    message_type="success"
                )
            except ValueError:
                return render_template(
                    "manage_songs.html",
                    songs=Song.query.all(),
                    message="Les vitesses doivent être des nombres valides",
                    message_type="error"
                )
            except Exception as e:
                db.session.rollback()
                return render_template(
                    "manage_songs.html",
                    songs=Song.query.all(),
                    message=f"Erreur lors de l'ajout de la chanson : {str(e)}",
                    message_type="error"
                )
        
        return render_template("manage_songs.html", songs=Song.query.all())

@app.route("/delete-song/<int:song_id>")
def delete_song(song_id):
    with app.app_context():
        try:
            song = Song.query.get_or_404(song_id)
            title = song.title
            db.session.delete(song)
            db.session.commit()
            return render_template(
                "manage_songs.html",
                songs=Song.query.all(),
                message=f"La chanson '{title}' a été supprimée avec succès !",
                message_type="success"
            )
        except Exception as e:
            db.session.rollback()
            return render_template(
                "manage_songs.html",
                songs=Song.query.all(),
                message=f"Erreur lors de la suppression de la chanson : {str(e)}",
                message_type="error"
            )

@app.route("/guitar-goals", methods=['GET', 'POST'])
def guitar_goals():
    with app.app_context():
        if request.method == 'POST':
            try:
                new_goal = GuitarGoal(
                    title=request.form['title'],
                    description=request.form['description'],
                    category=request.form['category'],
                    progress=int(request.form['progress']),
                    target_bpm=int(request.form['target_bpm']) if request.form['target_bpm'] else None
                )
                db.session.add(new_goal)
                db.session.commit()
                return render_template(
                    "guitar_goals.html",
                    goals=GuitarGoal.query.all(),
                    message="Objectif ajouté avec succès !",
                    message_type="success"
                )
            except Exception as e:
                db.session.rollback()
                return render_template(
                    "guitar_goals.html",
                    goals=GuitarGoal.query.all(),
                    message=f"Erreur lors de l'ajout de l'objectif : {str(e)}",
                    message_type="error"
                )
        
        return render_template("guitar_goals.html", goals=GuitarGoal.query.all())

@app.route("/edit-goal/<int:goal_id>", methods=['GET', 'POST'])
def edit_goal(goal_id):
    with app.app_context():
        goal = GuitarGoal.query.get_or_404(goal_id)
        
        if request.method == 'POST':
            try:
                goal.title = request.form['title']
                goal.description = request.form['description']
                goal.category = request.form['category']
                goal.progress = int(request.form['progress'])
                goal.target_bpm = int(request.form['target_bpm']) if request.form['target_bpm'] else None
                
                db.session.commit()
                return redirect(url_for('guitar_goals'))
            except Exception as e:
                db.session.rollback()
                return render_template(
                    "edit_goal.html",
                    goal=goal,
                    message=f"Erreur lors de la modification : {str(e)}",
                    message_type="error"
                )
        
        return render_template("edit_goal.html", goal=goal)

@app.route("/delete-goal/<int:goal_id>")
def delete_goal(goal_id):
    with app.app_context():
        try:
            goal = GuitarGoal.query.get_or_404(goal_id)
            db.session.delete(goal)
            db.session.commit()
            return render_template(
                "guitar_goals.html",
                goals=GuitarGoal.query.all(),
                message="Objectif supprimé avec succès !",
                message_type="success"
            )
        except Exception as e:
            db.session.rollback()
            return render_template(
                "guitar_goals.html",
                goals=GuitarGoal.query.all(),
                message=f"Erreur lors de la suppression : {str(e)}",
                message_type="error"
            )

@app.route("/update-song-speeds/<int:song_id>", methods=['POST'])
def update_song_speeds(song_id):
    with app.app_context():
        try:
            song = Song.query.get_or_404(song_id)
            data = request.get_json()

            song.min_speed = int(data['min_speed'])
            song.max_speed = int(data['max_speed'])
            song.challenge_speed = int(data['challenge_speed'])
            if 'intermediate_measures' in data:
                song.intermediate_measures = int(data['intermediate_measures'])
            
            db.session.commit()
            return jsonify({"message": "Vitesses mises à jour avec succès"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

@app.route("/update-song-prioritaire/<int:song_id>", methods=['POST'])
def update_song_prioritaire(song_id):
    with app.app_context():
        try:
            song = Song.query.get_or_404(song_id)
            data = request.get_json()
            song.prioritaire = int(data['prioritaire'])
            db.session.commit()
            return jsonify({"message": "Prioritaire mis à jour avec succès"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

@app.route("/manage-songsterr-links", methods=['GET', 'POST'])
def manage_songsterr_links():
    with app.app_context():
        message = None
        message_type = None
        if request.method == 'POST':
            song_name = request.form.get('song_name')
            songsterr_link = request.form.get('songsterr_link')
            try:
                # Obtenir le dernier ordre
                last_order = db.session.query(db.func.max(SongsterrLink.display_order)).scalar() or 0
                new_link = SongsterrLink(
                    song_name=song_name,
                    songsterr_link=songsterr_link,
                    display_order=last_order + 1
                )
                db.session.add(new_link)
                db.session.commit()
                message = f"Lien ajouté pour '{song_name}' !"
                message_type = "success"
            except Exception as e:
                db.session.rollback()
                message = f"Erreur lors de l'ajout : {str(e)}"
                message_type = "error"
        
        # Trier les liens par ordre
        links = SongsterrLink.query.order_by(SongsterrLink.display_order).all()
        return render_template("songsterr_links.html", links=links, message=message, message_type=message_type)

@app.route("/delete-songsterr-link/<song_name>", methods=['POST'])
def delete_songsterr_link(song_name):
    with app.app_context():
        message = None
        message_type = None
        try:
            link = SongsterrLink.query.filter_by(song_name=song_name).first_or_404()
            db.session.delete(link)
            db.session.commit()
            message = f"Lien supprimé pour '{song_name}' !"
            message_type = "success"
        except Exception as e:
            db.session.rollback()
            message = f"Erreur lors de la suppression : {str(e)}"
            message_type = "error"
        
        links = SongsterrLink.query.all()
        return render_template("songsterr_links.html", links=links, message=message, message_type=message_type)

@app.route("/upload-recording", methods=['POST'])
def upload_recording():
    file = request.files.get('file')
    filename = request.form.get('filename', 'recording.webm')
    if file:
        safe_name = secure_filename(filename)
        save_path = os.path.join('/app/data', safe_name)
        file.save(save_path)
        mp3_path = os.path.join('/app/data', os.path.splitext(safe_name)[0] + '.mp3')
        try:
            subprocess.run([
                'ffmpeg',
                '-y',
                '-i', save_path,
                '-vn',
                '-ar', '44100',
                '-ac', '2',
                '-b:a', '192k',
                mp3_path
            ], check=True)
        except Exception as e:
            print(f"Error converting to mp3: {e}")
        return jsonify({"message": "Fichier enregistré"}), 200
    return jsonify({"error": "Aucun fichier"}), 400

@app.route("/update-songsterr-links-order", methods=['POST'])
def update_songsterr_links_order():
    with app.app_context():
        try:
            data = request.get_json()
            new_order = data.get('order', [])
            
            # Mettre à jour l'ordre des liens
            for index, link_id in enumerate(new_order):
                link = SongsterrLink.query.get(link_id)
                if link:
                    link.display_order = index
            
            db.session.commit()
            return jsonify({"message": "Ordre mis à jour avec succès"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

@app.route("/update-songs-order-and-priority", methods=['POST'])
def update_songs_order_and_priority():
    with app.app_context():
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
            return jsonify({"message": "Ordre et priorité mis à jour"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
