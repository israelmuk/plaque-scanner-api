from flask import Flask, request, jsonify, send_from_directory, redirect, render_template
from scanner_openai import scan_plate
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CROPPED_FOLDER = 'uploads/cropped'
DB_PATH = 'scans.db'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CROPPED_FOLDER, exist_ok=True)

def save_to_db(plaque, proprietaire, image_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO history (plaque, proprietaire, image_path, timestamp) VALUES (?, ?, ?, ?)",
              (plaque, proprietaire, image_path, datetime.now().isoformat()))
    conn.commit()
    conn.close()

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
    image_url = ""
    if cropped_path and os.path.exists(cropped_path):
        image_url = "/plate-image/" + os.path.basename(cropped_path)
        result["image_url"] = image_url

    # Enregistrement dans la base de données
    save_to_db(result["plaque"], result["proprietaire"], image_url)

    return jsonify(result)

@app.route('/plate-image/<filename>')
def plate_image(filename):
    return send_from_directory('uploads/cropped', filename)

@app.route('/history')
def history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT plaque, proprietaire, image_path, timestamp FROM history ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template('history.html', rows=rows)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)