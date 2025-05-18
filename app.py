from flask import Flask, request, jsonify
from scanner import scan_plate
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/scan', methods=['POST'])
def scan():
    if 'image' not in request.files:
        return jsonify({"error": "Aucune image reçue"}), 400

    file = request.files['image']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    result = scan_plate(path)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)