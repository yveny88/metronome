from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    bpm = db.Column(db.Integer, nullable=False)
    beats_per_measure = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "bpm": self.bpm,
            "beats_per_measure": self.beats_per_measure
        } 