from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    bpm = db.Column(db.Integer, nullable=False)
    beats_per_measure = db.Column(db.Integer, default=4)
    min_speed = db.Column(db.Integer, default=60)  # Vitesse minimale recommandée
    max_speed = db.Column(db.Integer, default=120)  # Vitesse maximale recommandée
    challenge_speed = db.Column(db.Integer, default=140)  # Vitesse de défi
    prioritaire = db.Column(db.Integer, default=0)  # 0 ou 1 pour indiquer si la chanson est prioritaire

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "bpm": self.bpm,
            "beats_per_measure": self.beats_per_measure,
            "min_speed": self.min_speed,
            "max_speed": self.max_speed,
            "challenge_speed": self.challenge_speed,
            "prioritaire": self.prioritaire
        }



class GuitarGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    progress = db.Column(db.Integer, default=0)  # 0-100
    category = db.Column(db.String(50))  # 'technique' ou 'repertoire'
    target_bpm = db.Column(db.Integer)  # BPM cible si applicable

class SongsterrLink(db.Model):
    __tablename__ = 'songsterr_links'
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), nullable=False)
    songsterr_link = db.Column(db.String(200), nullable=False)
    display_order = db.Column(db.Integer, default=0)  # Renommé de 'order' à 'display_order'

    def to_dict(self):
        return {
            'id': self.id,
            'song_name': self.song_name,
            'songsterr_link': self.songsterr_link,
            'display_order': self.display_order
        }
