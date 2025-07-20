import sqlite3

# Mets ici le chemin correct vers ta base
db_path = "metronome.db"  # ou "/app/data/metronome.db" selon ton cas

conn = sqlite3.connect(db_path)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE song ADD COLUMN prioritaire BOOLEAN DEFAULT 0;")
    print("Colonne 'prioritaire' ajoutée avec succès.")
except Exception as e:
    print("Erreur ou colonne déjà existante :", e)

conn.commit()
conn.close()
