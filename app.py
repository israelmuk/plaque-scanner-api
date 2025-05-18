from flask import Flask, render_template, request, jsonify
from scanner import scan_plate
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    image = request.files.get('image')
    if not image:
        return jsonify({'error': 'Aucune image reçue'}), 400

    filename = datetime.now().strftime('%Y%m%d%H%M%S') + "_" + image.filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(path)

    result = scan_plate(path)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)