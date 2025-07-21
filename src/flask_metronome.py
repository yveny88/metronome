from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import os
import sys

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
        .nav-buttons {
            margin: 20px auto;
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        .nav-btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .nav-btn:hover {
            background-color: #2980b9;
        }
        .current-bpm {
            font-size: 48px;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 20px;
            text-align: center;
        }
        .countdown {
            font-size: 48px;
            font-weight: bold;
            color: #e74c3c;
            margin-top: 10px;
        }
        .columns {
            display: flex;
            gap: 40px;
            justify-content: center;
        }
        .song-column {
            flex: 1;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 18px 12px;
            min-width: 320px;
            box-shadow: 0 2px 8px #0001;
        }
        .column-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 18px;
            text-align: center;
            color: #1976d2;
        }
        .song-list {
            min-height: 60px;
        }
        .song-item {
            background: #fff;
            padding: 14px 12px;
            margin: 10px 0;
            border-radius: 6px;
            box-shadow: 0 1px 4px #0001;
            cursor: move;
        }
        .song-item.dragging {
            opacity: 0.5;
            background: #e3f0ff;
        }
        .song-info { flex: 1; display: flex; flex-direction: column; }
        .song-title { font-weight: bold; color: #2c3e50; font-size: 16px; }
        .song-bpm { color: #7f8c8d; margin-left: 8px; font-size: 14px; }
        .song-speeds { color: #444; font-size: 13px; }
        .apply-btn {
            display: block;
            margin: 0 auto 24px auto;
            padding: 12px 32px;
            background: #1976d2;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        .apply-btn:hover {
            background: #1256a3;
        }
        /* --- Formulaire joli --- */
        .add-song-form {
            background: #f8f9fa;
            padding: 28px 32px 22px 32px;
            border-radius: 10px;
            margin: 30px auto 30px auto;
            max-width: 420px;
            box-shadow: 0 2px 12px #0001;
            display: flex;
            flex-direction: column;
            gap: 18px;
        }
        .add-song-form h2 {
            font-size: 1.4em;
            color: #1976d2;
            margin-bottom: 10px;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .form-group label {
            color: #2c3e50;
            font-weight: 500;
        }
        .form-group input {
            padding: 10px 12px;
            border: 1px solid #cfd8dc;
            border-radius: 6px;
            font-size: 16px;
            background: #fff;
            transition: border 0.2s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #1976d2;
            background: #e3f0ff;
        }
        .submit-btn {
            background: #1976d2;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 12px 0;
            font-size: 17px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
            transition: background 0.2s;
        }
        .submit-btn:hover {
            background: #1256a3;
        }
    </style>
</head>
<body>
    <h1>🕒 Métronome Web Flask</h1>
    
    <!-- Boutons de navigation -->
    <div class="nav-buttons">
        <a href="/manage-songs" class="nav-btn">Gérer les chansons</a>
        <a href="/guitar-goals" class="nav-btn">Objectifs Guitare</a>
        <a href="/manage-songsterr-links" class="nav-btn">Liens Songsterr</a>
    </div>
    
    <!-- Menu déroulant des chansons -->
    <div class="song-selector">
        <select id="song-select">
            <option value="">Sélectionner une chanson...</option>
            {% for song in songs %}
            <option value="{{ song.bpm }}"
                    data-song-id="{{ song.id }}"
                    data-title="{{ song.title }}"
                    data-min-speed="{{ song.min_speed }}"
                    data-max-speed="{{ song.max_speed }}"
                    data-challenge-speed="{{ song.challenge_speed }}">
                {{ song.title }} ({{ song.bpm }} BPM)
            </option>
            {% endfor %}
        </select>
    </div>

    <!-- Informations de la chanson sélectionnée -->
    <div id="song-info" style="display: none; margin: 20px auto; max-width: 400px; padding: 15px; background: #f5f5f5; border-radius: 8px;">
        <div style="margin-bottom: 10px;">
            <strong>Titre :</strong> <span id="selected-title"></span>
        </div>
        <div style="margin-bottom: 10px;">
            <strong>Song BPM:</strong> <span id="selected-bpm"></span>
        </div>
        <div style="display: flex; justify-content: space-between; gap: 10px;">
            <div><strong>Min Speed:</strong> <span id="min-speed"></span></div>
            <div><strong>Max Speed:</strong> <span id="max-speed"></span></div>
            <div><strong>Challenge Speed:</strong> <span id="challenge-speed"></span></div>
        </div>
    </div>

    <div class="bpm-multi-container">
        <div class="bpm-col" id="col1">
            <input class="bpm-input" id="bpm-input-1" type="number" min="40" max="240" value="100" step="5" />
            <div class="bpm-scale" id="bpm-scale-1"></div>
            <div id="slider-dot-1"></div>
        </div>
        <div class="bpm-col" id="col2">
            <div id="intermediate-dots-1"></div>
        </div>
        <div class="bpm-col" id="col3">
            <input class="bpm-input" id="bpm-input-2" type="number" min="40" max="240" value="120" step="5" />
            <div class="bpm-scale" id="bpm-scale-2"></div>
            <div id="slider-dot-2"></div>
        </div>
        <div class="bpm-col" id="col4">
            <div id="intermediate-dots-2"></div>
        </div>
        <div class="bpm-col" id="col5">
            <input class="bpm-input" id="bpm-input-3" type="number" min="40" max="240" value="140" step="5" />
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
        <button id="full-workout">Full Workout</button>
        <button id="stop-btn" disabled>Arrêter</button>
        <button id="update-speeds" style="margin-left: 20px; background-color: #2ecc71; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Mettre à jour les vitesses</button>
        <button id="record-btn" style="margin-left: 20px;">Start Recording</button>
    </div>
    <div id="dot" class="dot">●</div>
    <div id="current-bpm" class="current-bpm">100 BPM</div>
    <div id="countdown" class="countdown"></div>
    <audio id="click" src="/static/metronome-85688.mp3"></audio>
    <script>
        console.log('JS chargé sur /manage-songs');
        const BPM_MIN = 40;
        const BPM_MAX = 240;
        const SCALE_HEIGHT = 400;
        const NUM_POINTS_1 = 10;
        const NUM_POINTS_2 = 5;
        const NUM_FINAL_POINTS = 10;

        const prioritizedSongs = [
            {% for song in songs %}
            {
                title: "{{ song.title }}",
                bpm: {{ song.bpm }},
                min_speed: {{ song.min_speed }},
                max_speed: {{ song.max_speed }},
                challenge_speed: {{ song.challenge_speed }}
            }{% if not loop.last %},{% endif %}
            {% endfor %}
        ];

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
        const fullWorkoutBtn = document.getElementById('full-workout');
        const stopBtn = document.getElementById('stop-btn');
        const click = document.getElementById('click');
        const countdownDiv = document.getElementById('countdown');
        const beatsInput = document.getElementById('beats');
        const interMeasuresInput = document.getElementById('interMeasures');

        const recordBtn = document.getElementById('record-btn');
        let mediaRecorder;
        let recordedChunks = [];

        recordBtn.onclick = async function() {
            if (recordBtn.textContent === 'Start Recording') {
                recordedChunks = [];
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => {
                    if (e.data.size > 0) recordedChunks.push(e.data);
                };
                mediaRecorder.onstop = async () => {
                    const blob = new Blob(recordedChunks, { type: 'audio/webm' });
                    const formData = new FormData();
                    formData.append('file', blob, 'recording.webm');
                    await fetch('/upload-recording', { method: 'POST', body: formData });
                };
                mediaRecorder.start();
                recordBtn.textContent = 'Stop Recording';
            } else {
                mediaRecorder.stop();
                recordBtn.textContent = 'Start Recording';
            }
        };
        
        // Variable pour contrôler l'arrêt du métronome
        let shouldStop = false;

        btn.onclick = async function() {
            if (isPlaying) return;
            isPlaying = true;
            shouldStop = false;
            btn.disabled = true;
            fullWorkoutBtn.disabled = true;
            stopBtn.disabled = false;
            btn.textContent = "En cours...";
            const bpm1 = parseInt(bpmInputs[0].value);
            await playCountdown(bpm1);
            if (shouldStop) { resetMetronome(); return; }
            playMetronomeSequence().then(() => {
                resetMetronome();
            });
        };

        fullWorkoutBtn.onclick = async function() {
            if (isPlaying) return;
            isPlaying = true;
            shouldStop = false;
            fullWorkoutBtn.disabled = true;
            btn.disabled = true;
            stopBtn.disabled = false;
            fullWorkoutBtn.textContent = "En cours...";

            for (let i = 0; i < prioritizedSongs.length; i++) {
                const song = prioritizedSongs[i];
                if (shouldStop) { resetMetronome(); return; }
                displaySongInfo(song);
                bpmInputs[0].value = song.min_speed;
                bpmInputs[1].value = song.max_speed;
                bpmInputs[2].value = song.challenge_speed;
                createSliders();
                createIntermediateDots1();
                createIntermediateDots2();
                createFinalDots();
                await playCountdown(parseInt(song.min_speed));
                if (shouldStop) { resetMetronome(); return; }
                await playMetronomeSequence();
                if (shouldStop) { resetMetronome(); return; }
                const nextSong = prioritizedSongs[i + 1];
                if (nextSong) {
                    displaySongInfo(nextSong);
                }
                await sleep(5000);
            }

            resetMetronome();
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
            fullWorkoutBtn.disabled = false;
            stopBtn.disabled = true;
            btn.textContent = "Start";
            fullWorkoutBtn.textContent = "Full Workout";
            stopBtn.textContent = "Arrêter";
            dot.classList.remove('active');
            sliderDots.forEach(d => d.classList.remove('active'));
            intermediateDots1.forEach(d => d.classList.remove('active'));
            intermediateDots2.forEach(d => d.classList.remove('active'));
            finalDots.forEach(d => d.classList.remove('active'));
            countdownDiv.textContent = '';
            displaySongInfo(null);
        }

        async function playCountdown(bpm) {
            const delay = 60000 / bpm;
            for (let i = 1; i <= 4; i++) {
                countdownDiv.textContent = i;
                dot.classList.add('active');
                click.currentTime = 0;
                click.play();
                await sleep(100);
                dot.classList.remove('active');
                await sleep(delay - 100);
            }
            countdownDiv.textContent = '';
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
            // Mettre à jour l'affichage du BPM actuel
            document.getElementById('current-bpm').textContent = `${bpm} BPM`;
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

        function displaySongInfo(song) {
            const songInfo = document.getElementById('song-info');
            if (song) {
                document.getElementById('selected-title').textContent = song.title;
                document.getElementById('selected-bpm').textContent = song.bpm;
                document.getElementById('min-speed').textContent = song.min_speed;
                document.getElementById('max-speed').textContent = song.max_speed;
                document.getElementById('challenge-speed').textContent = song.challenge_speed;
                songInfo.style.display = 'block';
            } else {
                songInfo.style.display = 'none';
            }
        }

        // Ajouter la gestion de l'affichage des informations de la chanson
        document.getElementById('song-select').addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (this.value) {
                // Mettre à jour l'affichage des informations
                displaySongInfo({
                    title: selectedOption.dataset.title,
                    bpm: this.value,
                    min_speed: selectedOption.dataset.minSpeed,
                    max_speed: selectedOption.dataset.maxSpeed,
                    challenge_speed: selectedOption.dataset.challengeSpeed
                });

                // Mettre à jour les valeurs des sliders
                bpmInputs[0].value = selectedOption.dataset.minSpeed;
                bpmInputs[1].value = selectedOption.dataset.maxSpeed;
                bpmInputs[2].value = selectedOption.dataset.challengeSpeed;

                // Mettre à jour l'affichage des sliders
                createSliders();
                createIntermediateDots1();
                createIntermediateDots2();
                createFinalDots();
            } else {
                displaySongInfo(null);
            }
        });

        // Ajouter la gestion du bouton de mise à jour des vitesses
        document.getElementById('update-speeds').addEventListener('click', async function() {
            const songSelect = document.getElementById('song-select');
            const selectedOption = songSelect.options[songSelect.selectedIndex];
            
            if (!selectedOption.value) {
                alert("Veuillez sélectionner une chanson d'abord");
                return;
            }

            const songId = selectedOption.dataset.songId;
            const minSpeed = bpmInputs[0].value;
            const maxSpeed = bpmInputs[1].value;
            const challengeSpeed = bpmInputs[2].value;

            try {
                const response = await fetch(`/update-song-speeds/${songId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        min_speed: minSpeed,
                        max_speed: maxSpeed,
                        challenge_speed: challengeSpeed
                    })
                });

                if (response.ok) {
                    alert('Les vitesses ont été mises à jour avec succès !');
                    // Mettre à jour les data-attributes de l'option
                    selectedOption.dataset.minSpeed = minSpeed;
                    selectedOption.dataset.maxSpeed = maxSpeed;
                    selectedOption.dataset.challengeSpeed = challengeSpeed;
                } else {
                    alert('Erreur lors de la mise à jour des vitesses');
                }
            } catch (error) {
                console.error('Erreur:', error);
                alert('Erreur lors de la mise à jour des vitesses');
            }
        });

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

        // Ajout gestion case à cocher prioritaire
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.prioritaire-checkbox').forEach(function(checkbox) {
                checkbox.addEventListener('change', function() {
                    const songId = this.getAttribute('data-song-id');
                    const prioritaire = this.checked ? 1 : 0;
                    fetch(`/update-song-prioritaire/${songId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ prioritaire })
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Réponse serveur:', data);
                        if (data.message) {
                            alert('Succès : ' + data.message);
                        } else if (data.error) {
                            alert('Erreur : ' + data.error);
                        }
                    })
                    .catch(error => {
                        alert('Erreur réseau : ' + error);
                    });
                });
            });
        });

        document.addEventListener('dragstart', function(e) {
            if (e.target.classList.contains('song-item')) {
                console.log('Drag start sur', e.target);
                draggedItem = e.target;
                e.target.classList.add('dragging');
            }
        });

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
        .columns {
            display: flex;
            gap: 40px;
            justify-content: center;
        }
        .song-column {
            flex: 1;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 18px 12px;
            min-width: 320px;
            box-shadow: 0 2px 8px #0001;
        }
        .column-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 18px;
            text-align: center;
            color: #1976d2;
        }
        .song-list {
            min-height: 60px;
        }
        .song-item {
            background: #fff;
            padding: 14px 12px;
            margin: 10px 0;
            border-radius: 6px;
            box-shadow: 0 1px 4px #0001;
            cursor: move;
        }
        .song-item.dragging {
            opacity: 0.5;
            background: #e3f0ff;
        }
        .song-info { flex: 1; display: flex; flex-direction: column; }
        .song-title { font-weight: bold; color: #2c3e50; font-size: 16px; }
        .song-bpm { color: #7f8c8d; margin-left: 8px; font-size: 14px; }
        .song-speeds { color: #444; font-size: 13px; }
        .apply-btn {
            display: block;
            margin: 0 auto 24px auto;
            padding: 12px 32px;
            background: #1976d2;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }
        .apply-btn:hover {
            background: #1256a3;
        }
        /* --- Formulaire joli --- */
        .add-song-form {
            background: #f8f9fa;
            padding: 28px 32px 22px 32px;
            border-radius: 10px;
            margin: 30px auto 30px auto;
            max-width: 420px;
            box-shadow: 0 2px 12px #0001;
            display: flex;
            flex-direction: column;
            gap: 18px;
        }
        .add-song-form h2 {
            font-size: 1.4em;
            color: #1976d2;
            margin-bottom: 10px;
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .form-group label {
            color: #2c3e50;
            font-weight: 500;
        }
        .form-group input {
            padding: 10px 12px;
            border: 1px solid #cfd8dc;
            border-radius: 6px;
            font-size: 16px;
            background: #fff;
            transition: border 0.2s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #1976d2;
            background: #e3f0ff;
        }
        .submit-btn {
            background: #1976d2;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 12px 0;
            font-size: 17px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
            transition: background 0.2s;
        }
        .submit-btn:hover {
            background: #1256a3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gestion des Chansons</h1>
        <a href="/" class="back-btn">Retour au Métronome</a>
        {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
        <h2>Ajouter une nouvelle chanson</h2>
        <form action="/manage-songs" method="POST" class="add-song-form">
            <h2>Ajouter une nouvelle chanson</h2>
            <div class="form-group">
                <label for="title">Titre de la chanson :</label>
                <input type="text" id="title" name="title" required>
            </div>
            <div class="form-group">
                <label for="bpm">BPM :</label>
                <input type="number" id="bpm" name="bpm" min="40" max="240" required>
            </div>
            <div class="form-group">
                <label for="min_speed">Vitesse minimale (BPM) :</label>
                <input type="number" id="min_speed" name="min_speed" min="40" max="240" value="60">
            </div>
            <div class="form-group">
                <label for="max_speed">Vitesse maximale (BPM) :</label>
                <input type="number" id="max_speed" name="max_speed" min="40" max="240" value="120">
            </div>
            <div class="form-group">
                <label for="challenge_speed">Vitesse de défi (BPM) :</label>
                <input type="number" id="challenge_speed" name="challenge_speed" min="40" max="240" value="140">
            </div>
            <button type="submit" class="submit-btn">Ajouter la chanson</button>
        </form>
        <button id="apply-changes-btn" class="apply-btn">Apply changes</button>
        <h2 style="margin-top:40px;">Liste des chansons</h2>
        <div class="columns">
            <div class="song-column" id="normal-column">
                <div class="column-title">Normal</div>
                <div class="song-list" id="normal-list">
                    {% for song in songs if not song.prioritaire %}
                    <div class="song-item" draggable="true" data-id="{{ song.id }}">
                        <div class="song-info">
                            <span class="song-title">{{ song.title }}</span>
                            <span class="song-bpm">{{ song.bpm }} BPM</span>
                            <div class="song-speeds">Vitesses : Min: {{ song.min_speed }} | Max: {{ song.max_speed }} | Défi: {{ song.challenge_speed }}</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            <div class="song-column" id="priority-column">
                <div class="column-title">Priority</div>
                <div class="song-list" id="priority-list">
                    {% for song in songs if song.prioritaire %}
                    <div class="song-item" draggable="true" data-id="{{ song.id }}">
                        <div class="song-info">
                            <span class="song-title">{{ song.title }}</span>
                            <span class="song-bpm">{{ song.bpm }} BPM</span>
                            <div class="song-speeds">Vitesses : Min: {{ song.min_speed }} | Max: {{ song.max_speed }} | Défi: {{ song.challenge_speed }}</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
    <script>
        function setupDragAndDrop(listId, otherListId, prioritaireValue) {
            const list = document.getElementById(listId);
            const otherList = document.getElementById(otherListId);
            let draggedItem = null;

            list.addEventListener('dragstart', function(e) {
                if (e.target.classList.contains('song-item')) {
                    draggedItem = e.target;
                    e.target.classList.add('dragging');
                }
            });
            list.addEventListener('dragend', function(e) {
                if (e.target.classList.contains('song-item')) {
                    e.target.classList.remove('dragging');
                    draggedItem = null;
                    sendOrderUpdate();
                }
            });
            list.addEventListener('dragover', function(e) {
                e.preventDefault();
                const afterElement = getDragAfterElement(list, e.clientY);
                const currentDragged = document.querySelector('.dragging');
                if (afterElement == null) {
                    list.appendChild(currentDragged);
                } else {
                    list.insertBefore(currentDragged, afterElement);
                }
            });
            list.addEventListener('drop', function(e) {
                e.preventDefault();
                if (draggedItem && draggedItem.parentNode !== list) {
                    list.appendChild(draggedItem);
                }
            });
            otherList.addEventListener('dragover', function(e) { e.preventDefault(); });
        }
        function getDragAfterElement(container, y) {
            const draggableElements = [...container.querySelectorAll('.song-item:not(.dragging)')];
            return draggableElements.reduce((closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;
                if (offset < 0 && offset > closest.offset) {
                    return { offset: offset, element: child };
                } else {
                    return closest;
                }
            }, { offset: Number.NEGATIVE_INFINITY }).element;
        }
        function sendOrderUpdate(showAlert = false) {
            const normalIds = Array.from(document.querySelectorAll('#normal-list .song-item')).map(item => item.dataset.id);
            const priorityIds = Array.from(document.querySelectorAll('#priority-list .song-item')).map(item => item.dataset.id);
            fetch('/update-songs-order-and-priority', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ normal: normalIds, priority: priorityIds })
            })
            .then(res => res.json())
            .then(data => {
                if (showAlert) {
                    if (data.message) {
                        alert('Changements appliqués !');
                    } else if (data.error) {
                        alert('Erreur : ' + data.error);
                    }
                }
            });
        }
        document.getElementById('apply-changes-btn').onclick = function() {
            sendOrderUpdate(true);
        };
        setupDragAndDrop('normal-list', 'priority-list', 0);
        setupDragAndDrop('priority-list', 'normal-list', 1);
    </script>
</body>
</html>
"""

# Template pour la page des objectifs guitare
GUITAR_GOALS_HTML = """
<!DOCTYPE html>
<html lang='fr'>
<head>
    <meta charset='UTF-8'>
    <title>Objectifs Guitare - Métronome</title>
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
        .goal-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .goal-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .goal-title {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .goal-description {
            color: #7f8c8d;
            margin-bottom: 10px;
        }
        .goal-progress {
            background: #ecf0f1;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
        }
        .progress-bar {
            background: #3498db;
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
        }
        .back-btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }
        .back-btn:hover {
            background-color: #2980b9;
        }
        .add-goal-form {
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
        .form-group input, .form-group select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #3498db;
        }
        .edit-btn {
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
            margin-left: 10px;
        }
        .edit-btn:hover {
            background-color: #27ae60;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🎸 Objectifs Guitare</h1>
        <a href="/" class="back-btn">Retour au Métronome</a>

        {% if message %}
        <div class="message {{ message_type }}">
            {{ message }}
        </div>
        {% endif %}

        <h2>Ajouter un nouvel objectif</h2>
        <form action="/guitar-goals" method="POST" class="add-goal-form">
            <div class="form-group">
                <label for="title">Titre de l'objectif :</label>
                <input type="text" id="title" name="title" required>
            </div>
            <div class="form-group">
                <label for="description">Description :</label>
                <input type="text" id="description" name="description" required>
            </div>
            <div class="form-group">
                <label for="category">Catégorie :</label>
                <select id="category" name="category" required>
                    <option value="technique">Technique</option>
                    <option value="repertoire">Répertoire</option>
                    <option value="theorie">Théorie</option>
                    <option value="citnk">CiTNK</option>
                    <option value="creativite">Créativité</option>
                </select>
            </div>
            <div class="form-group">
                <label for="target_bpm">BPM cible (optionnel) :</label>
                <input type="number" id="target_bpm" name="target_bpm" min="40" max="240">
            </div>
            <div class="form-group">
                <label for="progress">Progression (0-100) :</label>
                <input type="number" id="progress" name="progress" min="0" max="100" value="0" required>
            </div>
            <button type="submit" class="submit-btn">Ajouter l'objectif</button>
        </form>

        <div class="goal-section">
            <h2>Objectifs Techniques</h2>
            {% for goal in goals if goal.category == 'technique' %}
            <div class="goal-item">
                <div class="goal-title">{{ goal.title }}</div>
                <div class="goal-description">{{ goal.description }}</div>
                {% if goal.target_bpm %}
                <div class="goal-description">BPM cible : {{ goal.target_bpm }}</div>
                {% endif %}
                <div class="goal-progress">
                    <div class="progress-bar" style="width: {{ goal.progress }}%"></div>
                </div>
                <div style="margin-top: 10px;">
                    <a href="/edit-goal/{{ goal.id }}" class="edit-btn">Modifier</a>
                    <a href="/delete-goal/{{ goal.id }}" class="delete-btn" onclick="return confirm('Êtes-vous sûr de vouloir supprimer cet objectif ?')">Supprimer</a>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="goal-section">
            <h2>Répertoire</h2>
            {% for goal in goals if goal.category == 'repertoire' %}
            <div class="goal-item">
                <div class="goal-title">{{ goal.title }}</div>
                <div class="goal-description">{{ goal.description }}</div>
                {% if goal.target_bpm %}
                <div class="goal-description">BPM cible : {{ goal.target_bpm }}</div>
                {% endif %}
                <div class="goal-progress">
                    <div class="progress-bar" style="width: {{ goal.progress }}%"></div>
                </div>
                <div style="margin-top: 10px;">
                    <a href="/edit-goal/{{ goal.id }}" class="edit-btn">Modifier</a>
                    <a href="/delete-goal/{{ goal.id }}" class="delete-btn" onclick="return confirm('Êtes-vous sûr de vouloir supprimer cet objectif ?')">Supprimer</a>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="goal-section">
            <h2>Théorie</h2>
            {% for goal in goals if goal.category == 'theorie' %}
            <div class="goal-item">
                <div class="goal-title">{{ goal.title }}</div>
                <div class="goal-description">{{ goal.description }}</div>
                {% if goal.target_bpm %}
                <div class="goal-description">BPM cible : {{ goal.target_bpm }}</div>
                {% endif %}
                <div class="goal-progress">
                    <div class="progress-bar" style="width: {{ goal.progress }}%"></div>
                </div>
                <div style="margin-top: 10px;">
                    <a href="/edit-goal/{{ goal.id }}" class="edit-btn">Modifier</a>
                    <a href="/delete-goal/{{ goal.id }}" class="delete-btn" onclick="return confirm('Êtes-vous sûr de vouloir supprimer cet objectif ?')">Supprimer</a>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="goal-section">
            <h2>CiTNK</h2>
            {% for goal in goals if goal.category == 'citnk' %}
            <div class="goal-item">
                <div class="goal-title">{{ goal.title }}</div>
                <div class="goal-description">{{ goal.description }}</div>
                {% if goal.target_bpm %}
                <div class="goal-description">BPM cible : {{ goal.target_bpm }}</div>
                {% endif %}
                <div class="goal-progress">
                    <div class="progress-bar" style="width: {{ goal.progress }}%"></div>
                </div>
                <div style="margin-top: 10px;">
                    <a href="/edit-goal/{{ goal.id }}" class="edit-btn">Modifier</a>
                    <a href="/delete-goal/{{ goal.id }}" class="delete-btn" onclick="return confirm('Êtes-vous sûr de vouloir supprimer cet objectif ?')">Supprimer</a>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="goal-section">
            <h2>Créativité</h2>
            {% for goal in goals if goal.category == 'creativite' %}
            <div class="goal-item">
                <div class="goal-title">{{ goal.title }}</div>
                <div class="goal-description">{{ goal.description }}</div>
                {% if goal.target_bpm %}
                <div class="goal-description">BPM cible : {{ goal.target_bpm }}</div>
                {% endif %}
                <div class="goal-progress">
                    <div class="progress-bar" style="width: {{ goal.progress }}%"></div>
                </div>
                <div style="margin-top: 10px;">
                    <a href="/edit-goal/{{ goal.id }}" class="edit-btn">Modifier</a>
                    <a href="/delete-goal/{{ goal.id }}" class="delete-btn" onclick="return confirm('Êtes-vous sûr de vouloir supprimer cet objectif ?')">Supprimer</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

# Template pour l'édition d'un objectif
EDIT_GOAL_HTML = """
<!DOCTYPE html>
<html lang='fr'>
<head>
    <meta charset='UTF-8'>
    <title>Modifier l'objectif - Métronome</title>
    <style>
        /* ... mêmes styles que GUITAR_GOALS_HTML ... */
    </style>
</head>
<body>
    <div class="container">
        <h1>Modifier l'objectif</h1>
        <a href="/guitar-goals" class="back-btn">Retour aux objectifs</a>

        <form action="/edit-goal/{{ goal.id }}" method="POST" class="add-goal-form">
            <div class="form-group">
                <label for="title">Titre de l'objectif :</label>
                <input type="text" id="title" name="title" value="{{ goal.title }}" required>
            </div>
            <div class="form-group">
                <label for="description">Description :</label>
                <input type="text" id="description" name="description" value="{{ goal.description }}" required>
            </div>
            <div class="form-group">
                <label for="category">Catégorie :</label>
                <select id="category" name="category" required>
                    <option value="technique" {% if goal.category == 'technique' %}selected{% endif %}>Technique</option>
                    <option value="repertoire" {% if goal.category == 'repertoire' %}selected{% endif %}>Répertoire</option>
                    <option value="theorie" {% if goal.category == 'theorie' %}selected{% endif %}>Théorie</option>
                    <option value="citnk" {% if goal.category == 'citnk' %}selected{% endif %}>CiTNK</option>
                    <option value="creativite" {% if goal.category == 'creativite' %}selected{% endif %}>Créativité</option>
                </select>
            </div>
            <div class="form-group">
                <label for="target_bpm">BPM cible (optionnel) :</label>
                <input type="number" id="target_bpm" name="target_bpm" min="40" max="240" value="{{ goal.target_bpm or '' }}">
            </div>
            <div class="form-group">
                <label for="progress">Progression (0-100) :</label>
                <input type="number" id="progress" name="progress" min="0" max="100" value="{{ goal.progress }}" required>
            </div>
            <button type="submit" class="submit-btn">Mettre à jour l'objectif</button>
        </form>
    </div>
</body>
</html>
"""

SONGSTERR_LINKS_HTML = """
<!DOCTYPE html>
<html lang='fr'>
<head>
    <meta charset='UTF-8'>
    <title>Liens Songsterr</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1, h2 { color: #2c3e50; text-align: center; }
        .back-btn, .submit-btn { display: inline-block; padding: 10px 20px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; border: none; cursor: pointer; }
        .back-btn:hover, .submit-btn:hover { background-color: #2980b9; }
        .add-link-form { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #2c3e50; }
        .form-group input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        .form-group input:focus { outline: none; border-color: #3498db; }
        .message { padding: 10px; margin: 10px 0; border-radius: 4px; text-align: center; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        .link-list { margin: 20px 0; }
        .link-item {
            display: flex;
            align-items: center;
            background: #f8f9fa;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 6px #0001;
            padding: 12px 18px;
            transition: background 0.2s, box-shadow 0.2s;
        }
        .link-item:hover {
            background: #e3f0ff;
            box-shadow: 0 4px 12px #0002;
        }
        .drag-handle {
            font-size: 22px;
            margin-right: 18px;
            color: #b0b0b0;
            cursor: grab;
            user-select: none;
        }
        .link-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .song-title {
            font-weight: bold;
            color: #2c3e50;
            font-size: 17px;
        }
        .song-link {
            color: #1976d2;
            text-decoration: underline;
            font-size: 15px;
            word-break: break-all;
        }
        .delete-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 7px 16px;
            border-radius: 5px;
            font-size: 15px;
            margin-left: 18px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .delete-btn:hover {
            background: #c0392b;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gestion des liens Songsterr</h1>
        <a href="/" class="back-btn">Retour au Métronome</a>
        {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
        <h2>Ajouter un nouveau lien</h2>
        <form action="/manage-songsterr-links" method="POST" class="add-link-form">
            <div class="form-group">
                <label for="song_name">Nom de la chanson :</label>
                <input type="text" id="song_name" name="song_name" required>
            </div>
            <div class="form-group">
                <label for="songsterr_link">Lien Songsterr :</label>
                <input type="url" id="songsterr_link" name="songsterr_link" required>
            </div>
            <button type="submit" class="submit-btn">Ajouter le lien</button>
        </form>
        <h2>Liste des liens</h2>
        <div class="link-list" id="sortable-list">
            {% for link in links %}
            <div class="link-item" draggable="true" data-id="{{ link.id }}">
                <span class="drag-handle" title="Déplacer">☰</span>
                <div class="link-info">
                    <div class="song-title">{{ link.song_name }}</div>
                    <a class="song-link" href="{{ link.songsterr_link }}" target="_blank">
                        {{ link.songsterr_link }}
                        <span style="font-size: 14px;">🔗</span>
                    </a>
                </div>
                <form action="/delete-songsterr-link/{{ link.song_name }}" method="POST" style="margin:0;">
                    <button class="delete-btn" type="submit">Supprimer</button>
                </form>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const list = document.getElementById('sortable-list');
            let draggedItem = null;

            // Gestionnaire d'événements pour le début du drag
            list.addEventListener('dragstart', function(e) {
                if (e.target.classList.contains('song-item')) {
                    console.log('Drag start sur', e.target);
                    draggedItem = e.target;
                    e.target.classList.add('dragging');
                }
            });

            // Gestionnaire d'événements pour la fin du drag
            list.addEventListener('dragend', function(e) {
                e.target.classList.remove('dragging');
                draggedItem = null;
            });

            // Gestionnaire d'événements pendant le drag
            list.addEventListener('dragover', function(e) {
                e.preventDefault();
                const afterElement = getDragAfterElement(list, e.clientY);
                const currentDragged = document.querySelector('.dragging');
                if (afterElement == null) {
                    list.appendChild(currentDragged);
                } else {
                    list.insertBefore(currentDragged, afterElement);
                }
            });

            // Gestionnaire d'événements pour la fin du drop
            list.addEventListener('drop', function(e) {
                e.preventDefault();
                const items = [...list.querySelectorAll('.link-item')];
                const newOrder = items.map(item => item.dataset.id);
                
                // Envoyer le nouvel ordre au serveur
                fetch('/update-songsterr-links-order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ order: newOrder })
                });
            });

            // Fonction pour déterminer la position après le drag
            function getDragAfterElement(container, y) {
                const draggableElements = [...container.querySelectorAll('.link-item:not(.dragging)')];

                return draggableElements.reduce((closest, child) => {
                    const box = child.getBoundingClientRect();
                    const offset = y - box.top - box.height / 2;

                    if (offset < 0 && offset > closest.offset) {
                        return { offset: offset, element: child };
                    } else {
                        return closest;
                    }
                }, { offset: Number.NEGATIVE_INFINITY }).element;
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    with app.app_context():
        songs = Song.query.filter_by(prioritaire=1).all()
    return render_template_string(HTML, songs=songs)

@app.route("/manage-songs", methods=['GET', 'POST'])
def manage_songs():
    with app.app_context():
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
                    return render_template_string(
                        MANAGE_SONGS_HTML,
                        songs=Song.query.all(),
                        message="Le BPM doit être entre 40 et 240",
                        message_type="error"
                    )
                
                new_song = Song(
                    title=title,
                    bpm=bpm,
                    beats_per_measure=4,
                    min_speed=min_speed,
                    max_speed=max_speed,
                    challenge_speed=challenge_speed
                )
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
                    message="Les vitesses doivent être des nombres valides",
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
                return render_template_string(
                    GUITAR_GOALS_HTML,
                    goals=GuitarGoal.query.all(),
                    message="Objectif ajouté avec succès !",
                    message_type="success"
                )
            except Exception as e:
                db.session.rollback()
                return render_template_string(
                    GUITAR_GOALS_HTML,
                    goals=GuitarGoal.query.all(),
                    message=f"Erreur lors de l'ajout de l'objectif : {str(e)}",
                    message_type="error"
                )
        
        return render_template_string(GUITAR_GOALS_HTML, goals=GuitarGoal.query.all())

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
                return render_template_string(
                    EDIT_GOAL_HTML,
                    goal=goal,
                    message=f"Erreur lors de la modification : {str(e)}",
                    message_type="error"
                )
        
        return render_template_string(EDIT_GOAL_HTML, goal=goal)

@app.route("/delete-goal/<int:goal_id>")
def delete_goal(goal_id):
    with app.app_context():
        try:
            goal = GuitarGoal.query.get_or_404(goal_id)
            db.session.delete(goal)
            db.session.commit()
            return render_template_string(
                GUITAR_GOALS_HTML,
                goals=GuitarGoal.query.all(),
                message="Objectif supprimé avec succès !",
                message_type="success"
            )
        except Exception as e:
            db.session.rollback()
            return render_template_string(
                GUITAR_GOALS_HTML,
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
        return render_template_string(SONGSTERR_LINKS_HTML, links=links, message=message, message_type=message_type)

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
        return render_template_string(SONGSTERR_LINKS_HTML, links=links, message=message, message_type=message_type)

@app.route("/upload-recording", methods=['POST'])
def upload_recording():
    file = request.files.get('file')
    if file:
        save_path = os.path.join('/app/data', 'recording.webm')
        file.save(save_path)
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
