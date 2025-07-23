import sqlite3
import os

DB_PATH = os.environ.get('DB_PATH', 'metronome.db')

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(song)")
existing_columns = {row[1] for row in cur.fetchall()}

columns_to_add = {
    'intermediate_measures': 'INTEGER DEFAULT 1',
    'min_speed': 'INTEGER DEFAULT 60',
    'max_speed': 'INTEGER DEFAULT 120',
    'challenge_speed': 'INTEGER DEFAULT 140',
    'prioritaire': 'INTEGER DEFAULT 0'
}

for column, col_def in columns_to_add.items():
    if column not in existing_columns:
        try:
            cur.execute(f"ALTER TABLE song ADD COLUMN {column} {col_def}")
            print(f"Colonne '{column}' ajoutée.")
        except sqlite3.OperationalError as e:
            print(f"Erreur lors de l'ajout de {column}: {e}")
    else:
        print(f"Colonne '{column}' déjà présente")

conn.commit()
conn.close()
