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

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "bpm": self.bpm,
            "beats_per_measure": self.beats_per_measure,
            "min_speed": self.min_speed,
            "max_speed": self.max_speed,
            "challenge_speed": self.challenge_speed
        }

class GuitarGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    progress = db.Column(db.Integer, default=0)  # 0-100
    category = db.Column(db.String(50))  # 'technique' ou 'repertoire'
    target_bpm = db.Column(db.Integer)  # BPM cible si applicable 