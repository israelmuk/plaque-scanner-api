import cv2
import pytesseract
import os
import json
import re

def scan_plate(image_path):
    if not os.path.exists(image_path):
        return {"plaque": "", "proprietaire": "Image non trouvée"}

    img = cv2.imread(image_path)

    # Prétraitement de l'image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    raw_text = pytesseract.image_to_string(thresh, config=config)
    clean_text = "".join(raw_text.split())

    match = re.search(r'\b\d{4}[A-Z]{2}\d{2}\b', clean_text)
    plate_number = match.group(0) if match else clean_text

    owner = "Inconnu"
    if os.path.exists("owners.json"):
        with open("owners.json", "r") as f:
            data = json.load(f)
            owner = data.get(plate_number, "Inconnu")

    return {"plaque": plate_number, "proprietaire": owner}