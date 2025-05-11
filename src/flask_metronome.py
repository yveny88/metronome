from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import os
import sys

# Ajouter le répertoire src au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import db, Song
from src.routes.song_routes import song_bp, init_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metronome.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser la base de données
db.init_app(app)

# Enregistrer les blueprints
app.register_blueprint(song_bp)

# Créer les tables de la base de données et initialiser avec des données
# seulement si la base n'existe pas
with app.app_context():
    if not os.path.exists('metronome.db'):
        db.create_all()
        init_db()  # Ajouter les chansons initiales seulement si la base est vide

HTML = """
<!DOCTYPE html>
<html lang='fr'>
<head>
    <meta charset='UTF-8'>
    <title>Métronome Web Flask</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 30px; }
        .bpm-multi-container {
            display: flex;
            justify-content: center;
            align-items: flex-end;
            gap: 40px;
            margin-bottom: 30px;
        }
        .bpm-col {
            position: relative;
            width: 80px;
            height: 420px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .bpm-input {
            margin-bottom: 5px;
            width: 60px;
            text-align: center;
            font-size: 15px;
        }
        .bpm-scale {
            position: relative;
            width: 60px;
            height: 400px;
            border-left: 2px solid #888;
            background: linear-gradient(to top, #f8f8f8 0%, #e0e0e0 100%);
        }
        .bpm-tick {
            position: absolute;
            left: 0;
            width: 20px;
            height: 1px;
            background: #888;
        }
        .bpm-label {
            position: absolute;
            left: 25px;
            font-size: 12px;
            color: #444;
            transform: translateY(50%);
        }
        .slider-dot {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            z-index: 2;
        }
        .slider-dot .slider-circle {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #3498db;
            border: 3px solid #2980b9;
            margin-right: 10px;
            transition: border 0.2s, background 0.2s;
        }
        .slider-dot.active .slider-circle {
            background: #e74c3c;
            border: 3px solid #c0392b;
        }
        .slider-dot .slider-bpm-label {
            font-weight: bold;
            font-size: 15px;
            color: #222;
            min-width: 40px;
            text-align: left;
            margin-left: 10px;
        }
        .bpm-slider {
            margin-top: 10px;
            width: 60px;
        }
        .intermediate-dot {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            z-index: 1;
        }
        .intermediate-dot .dot-circle {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #bbb;
            border: 2px solid #eee;
            margin-right: 8px;
            transition: background 0.2s, border 0.2s;
        }
        .intermediate-dot.active .dot-circle {
            background: #e74c3c;
            border: 2px solid #c0392b;
        }
        .intermediate-dot .dot-bpm-label {
            font-size: 13px;
            color: #444;
            min-width: 30px;
            text-align: left;
        }
        .final-dots-row {
            position: absolute;
            left: 100px;
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            gap: 10px;
        }
        .final-dot {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .final-dot .dot-circle {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #bbb;
            border: 2px solid #eee;
            margin-bottom: 2px;
            transition: background 0.2s, border 0.2s;
        }
        .final-dot.active .dot-circle {
            background: #e74c3c;
            border: 2px solid #c0392b;
        }
        .final-dot .dot-bpm-label {
            font-size: 13px;
            color: #444;
            min-width: 30px;
            text-align: center;
        }
        .dot { font-size: 80px; color: gray; transition: color 0.1s; }
        .dot.active { color: red; }
        .controls { margin: 30px; }
        #start-stop { font-size: 1.2em; padding: 10px 30px; }
        .song-selector {
            margin: 20px auto;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 8px;
            max-width: 400px;
        }
        .song-selector select {
            width: 100%;
            padding: 8px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
        }
        .song-selector select:focus {
            outline: none;
            border-color: #3498db;
        }
        .manage-songs-btn {
            display: inline-block;
            margin: 20px auto;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .manage-songs-btn:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <h1>🕒 Métronome Web Flask</h1>
    
    <!-- Bouton de gestion des chansons -->
    <a href="/manage-songs" class="manage-songs-btn">Gérer les chansons</a>
    
    <!-- Menu déroulant des chansons -->
    <div class="song-selector">
        <select id="song-select">
            <option value="">Sélectionner une chanson...</option>
            {% for song in songs %}
            <option value="{{ song.bpm }}">{{ song.title }} ({{ song.bpm }} BPM)</option>
            {% endfor %}
        </select>
    </div>

    <div class="bpm-multi-container">
        <div class="bpm-col" id="col1">
            <input class="bpm-input" id="bpm-input-1" type="number" min="40" max="208" value="100" step="5" />
            <div class="bpm-scale" id="bpm-scale-1"></div>
            <div id="slider-dot-1"></div>
        </div>
        <div class="bpm-col" id="col2">
            <div id="intermediate-dots-1"></div>
        </div>
        <div class="bpm-col" id="col3">
            <input class="bpm-input" id="bpm-input-2" type="number" min="40" max="208" value="120" step="5" />
            <div class="bpm-scale" id="bpm-scale-2"></div>
            <div id="slider-dot-2"></div>
        </div>
        <div class="bpm-col" id="col4">
            <div id="intermediate-dots-2"></div>
        </div>
        <div class="bpm-col" id="col5">
            <input class="bpm-input" id="bpm-input-3" type="number" min="40" max="208" value="140" step="5" />
            <div class="bpm-scale" id="bpm-scale-3"></div>
            <div id="slider-dot-3"></div>
            <div style="position: relative; width: 100%; height: 400px;">
                <div id="final-dots" class="final-dots-row"></div>
            </div>
        </div>
    </div>
    <div>
        <label for="beats">Temps par mesure : </label>
        <input type="number" id="beats" min="1" max="12" value="4" style="width: 50px;" />
        &nbsp;&nbsp;
        <label for="interMeasures">Mesures par point intermédiaire : </label>
        <input type="number" id="interMeasures" min="1" max="8" value="1" style="width: 50px;" />
    </div>
    <div class="controls">
        <button id="start-stop">Start</button>
        <button id="stop-btn" disabled>Arrêter</button>
    </div>
    <div id="dot" class="dot">●</div>
    <audio id="click" src="/static/metronome-85688.mp3"></audio>
    <script>
        const BPM_MIN = 40;
        const BPM_MAX = 208;
        const SCALE_HEIGHT = 400;
        const NUM_POINTS_1 = 10;
        const NUM_POINTS_2 = 5;
        const NUM_FINAL_POINTS = 10;

        function createScale(scaleId) {
            const scale = document.getElementById(scaleId);
            scale.innerHTML = '';
            for (let bpm = BPM_MIN; bpm <= BPM_MAX; bpm += 10) {
                const y = SCALE_HEIGHT - ((bpm - BPM_MIN) / (BPM_MAX - BPM_MIN)) * SCALE_HEIGHT;
                const tick = document.createElement('div');
                tick.className = 'bpm-tick';
                tick.style.top = `${y}px`;
                tick.style.height = '1px';
                scale.appendChild(tick);
                const label = document.createElement('div');
                label.className = 'bpm-label';
                label.style.top = `${y-7}px`;
                label.textContent = bpm;
                scale.appendChild(label);
            }
        }
        createScale('bpm-scale-1');
        createScale('bpm-scale-2');
        createScale('bpm-scale-3');

        const bpmInputs = [
            document.getElementById('bpm-input-1'),
            document.getElementById('bpm-input-2'),
            document.getElementById('bpm-input-3')
        ];
        const sliderDotDivs = [
            document.getElementById('slider-dot-1'),
            document.getElementById('slider-dot-2'),
            document.getElementById('slider-dot-3')
        ];
        const intermediateDots1Div = document.getElementById('intermediate-dots-1');
        const intermediateDots2Div = document.getElementById('intermediate-dots-2');
        const finalDotsDiv = document.getElementById('final-dots');
        let sliderDots = [];
        let intermediateDots1 = [];
        let intermediateDots2 = [];
        let finalDots = [];

        function bpmToY(bpm) {
            return SCALE_HEIGHT - ((bpm - BPM_MIN) / (BPM_MAX - BPM_MIN)) * SCALE_HEIGHT;
        }

        function createSliders() {
            sliderDots = [];
            for (let i = 0; i < 3; i++) {
                sliderDotDivs[i].innerHTML = '';
                const bpm = parseInt(bpmInputs[i].value);
                const dot = document.createElement('div');
                dot.className = 'slider-dot';
                dot.style.top = `${bpmToY(bpm)}px`;
                dot.innerHTML = `
                    <div class="slider-circle"></div>
                    <span class="slider-bpm-label">${bpm}</span>
                `;
                sliderDotDivs[i].appendChild(dot);
                sliderDots.push(dot);
            }
        }
        createSliders();

        function createIntermediateDots1() {
            intermediateDots1Div.innerHTML = '';
            intermediateDots1 = [];
            const bpm1 = parseInt(bpmInputs[0].value);
            const bpm2 = parseInt(bpmInputs[1].value);
            for (let i = 1; i <= NUM_POINTS_1; i++) {
                let bpm = bpm1 + (bpm2 - bpm1) * (i / (NUM_POINTS_1 + 1));
                bpm = Math.round(bpm);
                const y = bpmToY(bpm);
                const dot = document.createElement('div');
                dot.className = 'intermediate-dot';
                dot.style.top = `${y}px`;
                dot.innerHTML = `
                    <div class="dot-circle"></div>
                    <span class="dot-bpm-label">${bpm}</span>
                `;
                intermediateDots1Div.appendChild(dot);
                intermediateDots1.push(dot);
            }
        }
        createIntermediateDots1();

        function createIntermediateDots2() {
            intermediateDots2Div.innerHTML = '';
            intermediateDots2 = [];
            const bpm2 = parseInt(bpmInputs[1].value);
            const bpm3 = parseInt(bpmInputs[2].value);
            for (let i = 1; i <= NUM_POINTS_2; i++) {
                let bpm = bpm2 + (bpm3 - bpm2) * (i / (NUM_POINTS_2 + 1));
                bpm = Math.round(bpm);
                const y = bpmToY(bpm);
                const dot = document.createElement('div');
                dot.className = 'intermediate-dot';
                dot.style.top = `${y}px`;
                dot.innerHTML = `
                    <div class="dot-circle"></div>
                    <span class="dot-bpm-label">${bpm}</span>
                `;
                intermediateDots2Div.appendChild(dot);
                intermediateDots2.push(dot);
            }
        }
        createIntermediateDots2();

        function createFinalDots() {
            finalDotsDiv.innerHTML = '';
            finalDots = [];
            const bpm3 = parseInt(bpmInputs[2].value);
            const y = bpmToY(bpm3);
            finalDotsDiv.style.position = 'absolute';
            finalDotsDiv.style.left = '100px';
            finalDotsDiv.style.top = `${y - 9}px`;
            for (let i = 0; i < NUM_FINAL_POINTS; i++) {
                const dot = document.createElement('div');
                dot.className = 'final-dot';
                dot.innerHTML = `
                    <div class="dot-circle"></div>
                    <span class="dot-bpm-label">${bpm3}</span>
                `;
                finalDotsDiv.appendChild(dot);
                finalDots.push(dot);
            }
        }
        createFinalDots();

        for (let i = 0; i < 3; i++) {
            bpmInputs[i].oninput = function() {
                let val = Math.max(BPM_MIN, Math.min(BPM_MAX, parseInt(this.value) || BPM_MIN));
                this.value = val;
                createSliders();
                createIntermediateDots1();
                createIntermediateDots2();
                createFinalDots();
            };
        }

        let isPlaying = false;
        const dot = document.getElementById('dot');
        const btn = document.getElementById('start-stop');
        const stopBtn = document.getElementById('stop-btn');
        const click = document.getElementById('click');
        const beatsInput = document.getElementById('beats');
        const interMeasuresInput = document.getElementById('interMeasures');
        
        // Variable pour contrôler l'arrêt du métronome
        let shouldStop = false;

        btn.onclick = function() {
            if (isPlaying) return;
            isPlaying = true;
            shouldStop = false;
            btn.disabled = true;
            stopBtn.disabled = false;
            btn.textContent = "En cours...";
            playMetronomeSequence().then(() => {
                resetMetronome();
            });
        };
        
        stopBtn.onclick = function() {
            shouldStop = true;
            stopBtn.disabled = true;
            stopBtn.textContent = "Arrêt en cours...";
        };
        
        function resetMetronome() {
            isPlaying = false;
            shouldStop = false;
            btn.disabled = false;
            stopBtn.disabled = true;
            btn.textContent = "Start";
            stopBtn.textContent = "Arrêter";
            dot.classList.remove('active');
            sliderDots.forEach(d => d.classList.remove('active'));
            intermediateDots1.forEach(d => d.classList.remove('active'));
            intermediateDots2.forEach(d => d.classList.remove('active'));
            finalDots.forEach(d => d.classList.remove('active'));
        }

        async function playMetronomeSequence() {
            const bpm1 = parseInt(bpmInputs[0].value);
            const bpm2 = parseInt(bpmInputs[1].value);
            const bpm3 = parseInt(bpmInputs[2].value);
            const beatsPerMeasure = parseInt(beatsInput.value);
            const interMeasures = parseInt(interMeasuresInput.value);
            
            // Vérifier si on doit arrêter
            if (shouldStop) {
                return;
            }

            // BPM intermédiaires
            let intermediateBpms1 = [];
            for (let i = 1; i <= NUM_POINTS_1; i++) {
                let bpm = bpm1 + (bpm2 - bpm1) * (i / (NUM_POINTS_1 + 1));
                intermediateBpms1.push(Math.round(bpm));
            }
            let intermediateBpms2 = [];
            for (let i = 1; i <= NUM_POINTS_2; i++) {
                let bpm = bpm2 + (bpm3 - bpm2) * (i / (NUM_POINTS_2 + 1));
                intermediateBpms2.push(Math.round(bpm));
            }

            // 2 mesures à BPM1
            sliderDots[0].classList.add('active');
            await playMeasures(bpm1, beatsPerMeasure, interMeasures);
            if (shouldStop) { resetMetronome(); return; }
            sliderDots[0].classList.remove('active');

            // Mesures intermédiaires 1
            for (let i = 0; i < NUM_POINTS_1; i++) {
                if (shouldStop) { resetMetronome(); return; }
                intermediateDots1[i].classList.add('active');
                await playMeasures(intermediateBpms1[i], beatsPerMeasure, interMeasures);
                if (shouldStop) { resetMetronome(); return; }
                intermediateDots1[i].classList.remove('active');
            }

            // 2 mesures à BPM2
            sliderDots[1].classList.add('active');
            await playMeasures(bpm2, beatsPerMeasure, interMeasures);
            if (shouldStop) { resetMetronome(); return; }
            sliderDots[1].classList.remove('active');

            // Mesures intermédiaires 2
            for (let i = 0; i < NUM_POINTS_2; i++) {
                if (shouldStop) { resetMetronome(); return; }
                intermediateDots2[i].classList.add('active');
                await playMeasures(intermediateBpms2[i], beatsPerMeasure, interMeasures);
                if (shouldStop) { resetMetronome(); return; }
                intermediateDots2[i].classList.remove('active');
            }

            // 2 mesures à BPM3
            sliderDots[2].classList.add('active');
            await playMeasures(bpm3, beatsPerMeasure, interMeasures);
            if (shouldStop) { resetMetronome(); return; }
            sliderDots[2].classList.remove('active');

            // 10 mesures à BPM3 (final)
            for (let i = 0; i < NUM_FINAL_POINTS; i++) {
                if (shouldStop) { resetMetronome(); return; }
                finalDots[i].classList.add('active');
                await playMeasures(bpm3, beatsPerMeasure, interMeasures);
                if (shouldStop) { resetMetronome(); return; }
                finalDots[i].classList.remove('active');
            }
        }

        async function playMeasures(bpm, beatsPerMeasure, numMeasures) {
            const delay = 60000 / bpm;
            for (let m = 0; m < numMeasures; m++) {
                if (shouldStop) return;
                for (let b = 0; b < beatsPerMeasure; b++) {
                    if (shouldStop) return;
                    dot.classList.add('active');
                    click.currentTime = 0;
                    click.play();
                    await sleep(100);
                    dot.classList.remove('active');
                    await sleep(delay - 100);
                }
            }
        }

        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    </script>
</body>
</html>
"""

# Template pour la page de gestion des chansons
MANAGE_SONGS_HTML = """
<!DOCTYPE html>
<html lang='fr'>
<head>
    <meta charset='UTF-8'>
    <title>Gestion des Chansons - Métronome</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1, h2 { 
            color: #2c3e50;
            text-align: center;
        }
        .song-list {
            margin: 20px 0;
        }
        .song-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .song-info {
            flex-grow: 1;
        }
        .song-title {
            font-weight: bold;
            color: #2c3e50;
        }
        .song-bpm {
            color: #7f8c8d;
            margin-left: 10px;
        }
        .back-btn, .submit-btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            border: none;
            cursor: pointer;
        }
        .back-btn:hover, .submit-btn:hover {
            background-color: #2980b9;
        }
        .add-song-form {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #2c3e50;
        }
        .form-group input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #3498db;
        }
        .message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            text-align: center;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
        .delete-btn {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        .delete-btn:hover {
            background-color: #c0392b;
        }
        .confirm-dialog {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        .confirm-dialog-backdrop {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        }
        .confirm-dialog-buttons {
            margin-top: 20px;
            text-align: right;
        }
        .confirm-dialog-buttons button {
            margin-left: 10px;
        }
        .cancel-btn {
            background-color: #95a5a6;
        }
        .cancel-btn:hover {
            background-color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gestion des Chansons</h1>
        <a href="/" class="back-btn">Retour au Métronome</a>
        
        {% if message %}
        <div class="message {{ message_type }}">
            {{ message }}
        </div>
        {% endif %}

        <h2>Ajouter une nouvelle chanson</h2>
        <form action="/manage-songs" method="POST" class="add-song-form">
            <div class="form-group">
                <label for="title">Titre de la chanson :</label>
                <input type="text" id="title" name="title" required>
            </div>
            <div class="form-group">
                <label for="bpm">BPM :</label>
                <input type="number" id="bpm" name="bpm" min="40" max="208" required>
            </div>
            <button type="submit" class="submit-btn">Ajouter la chanson</button>
        </form>
        
        <h2>Liste des chansons</h2>
        <div class="song-list">
            {% for song in songs %}
            <div class="song-item">
                <div class="song-info">
                    <span class="song-title">{{ song.title }}</span>
                    <span class="song-bpm">{{ song.bpm }} BPM</span>
                </div>
                <button class="delete-btn" onclick="confirmDelete('{{ song.id }}', '{{ song.title }}')">Supprimer</button>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- Dialog de confirmation -->
    <div class="confirm-dialog-backdrop" id="confirmDialogBackdrop"></div>
    <div class="confirm-dialog" id="confirmDialog">
        <h3>Confirmer la suppression</h3>
        <p>Êtes-vous sûr de vouloir supprimer la chanson "<span id="songTitle"></span>" ?</p>
        <div class="confirm-dialog-buttons">
            <button class="back-btn cancel-btn" onclick="hideConfirmDialog()">Annuler</button>
            <button class="delete-btn" id="confirmDeleteBtn">Supprimer</button>
        </div>
    </div>

    <script>
        function confirmDelete(songId, songTitle) {
            document.getElementById('songTitle').textContent = songTitle;
            document.getElementById('confirmDialog').style.display = 'block';
            document.getElementById('confirmDialogBackdrop').style.display = 'block';
            
            document.getElementById('confirmDeleteBtn').onclick = function() {
                window.location.href = `/delete-song/${songId}`;
            };
        }

        function hideConfirmDialog() {
            document.getElementById('confirmDialog').style.display = 'none';
            document.getElementById('confirmDialogBackdrop').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    with app.app_context():
        songs = Song.query.all()
    return render_template_string(HTML, songs=songs)

@app.route("/manage-songs", methods=['GET', 'POST'])
def manage_songs():
    with app.app_context():
        if request.method == 'POST':
            title = request.form.get('title')
            bpm = request.form.get('bpm')
            
            try:
                bpm = int(bpm)
                if not (40 <= bpm <= 208):
                    return render_template_string(
                        MANAGE_SONGS_HTML,
                        songs=Song.query.all(),
                        message="Le BPM doit être entre 40 et 208",
                        message_type="error"
                    )
                
                new_song = Song(title=title, bpm=bpm, beats_per_measure=4)
                db.session.add(new_song)
                db.session.commit()
                
                return render_template_string(
                    MANAGE_SONGS_HTML,
                    songs=Song.query.all(),
                    message=f"La chanson '{title}' a été ajoutée avec succès !",
                    message_type="success"
                )
            except ValueError:
                return render_template_string(
                    MANAGE_SONGS_HTML,
                    songs=Song.query.all(),
                    message="Le BPM doit être un nombre valide",
                    message_type="error"
                )
            except Exception as e:
                db.session.rollback()
                return render_template_string(
                    MANAGE_SONGS_HTML,
                    songs=Song.query.all(),
                    message=f"Erreur lors de l'ajout de la chanson : {str(e)}",
                    message_type="error"
                )
        
        return render_template_string(MANAGE_SONGS_HTML, songs=Song.query.all())

@app.route("/delete-song/<int:song_id>")
def delete_song(song_id):
    with app.app_context():
        try:
            song = Song.query.get_or_404(song_id)
            title = song.title
            db.session.delete(song)
            db.session.commit()
            return render_template_string(
                MANAGE_SONGS_HTML,
                songs=Song.query.all(),
                message=f"La chanson '{title}' a été supprimée avec succès !",
                message_type="success"
            )
        except Exception as e:
            db.session.rollback()
            return render_template_string(
                MANAGE_SONGS_HTML,
                songs=Song.query.all(),
                message=f"Erreur lors de la suppression de la chanson : {str(e)}",
                message_type="error"
            )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False) 