FROM python:3.9-slim

# Installation des dépendances système nécessaires pour pygame et sqlite3
RUN apt-get update && apt-get install -y \
    python3-tk \
    libsdl2-2.0-0 \
    libsdl2-mixer-2.0-0 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src/ ./src/

EXPOSE 5000

CMD ["python", "src/flask_metronome.py"] 