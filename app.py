from flask import Flask, request, jsonify, send_from_directory, redirect, render_template
from scanner import scan_plate
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CROPPED_FOLDER = 'uploads/cropped'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CROPPED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return redirect('/scan')

@app.route('/scan')
def scan():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    image = request.files.get('image')
    if not image:
        return jsonify({"error": "Aucune image reçue"}), 400

    filename = datetime.now().strftime('%Y%m%d%H%M%S_') + image.filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(path)

    result = scan_plate(path)
    cropped_path = result.pop("cropped", None)
    if cropped_path and os.path.exists(cropped_path):
        result["image_url"] = "/plate-image/" + os.path.basename(cropped_path)

    return jsonify(result)

@app.route('/plate-image/<filename>')
def plate_image(filename):
    return send_from_directory('uploads/cropped', filename)