import os
from flask import Blueprint, render_template, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename

recordings_bp = Blueprint('recordings', __name__)

@recordings_bp.route('/recordings')
def list_recordings():
    recordings_dir = '/app/data'
    try:
        files = [f for f in os.listdir(recordings_dir) if f.lower().endswith(('.webm', '.wav', '.mp3'))]
    except FileNotFoundError:
        files = []
    return render_template('recordings.html', recordings=files, message=None, message_type=None)

@recordings_bp.route('/data/<path:filename>')
def data_file(filename):
    return send_from_directory('/app/data', filename)

@recordings_bp.route('/delete-recording/<path:filename>')
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
    return render_template('recordings.html', recordings=files, message=message, message_type=message_type)

@recordings_bp.route('/upload-recording', methods=['POST'])
def upload_recording():
    file = request.files.get('file')
    filename = request.form.get('filename', 'recording.webm')
    if file:
        safe_name = secure_filename(filename)
        save_path = os.path.join('/app/data', safe_name)
        file.save(save_path)
        return jsonify({"message": "Fichier enregistré"}), 200
    return jsonify({"error": "Aucun fichier"}), 400
