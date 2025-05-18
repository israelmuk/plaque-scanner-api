import cv2
import pytesseract
import os
import json
import re
import difflib

def extraire_plaque_valide(text):
    # Filtre les textes pour ne garder que des plaques au format 1234AB10
    matches = re.findall(r'\b\d{4}[A-Z]{2}\d{2}\b', text)
    return matches[0] if matches else ""

def scan_plate(image_path):
    if not os.path.exists(image_path):
        return {"plaque": "", "proprietaire": "Image non trouvée"}

    # Lire l'image
    img = cv2.imread(image_path)

    # Améliorer l’image : gris, filtre, contraste
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    gray = cv2.equalizeHist(gray)  # améliore le contraste
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # OCR : lire uniquement chiffres et lettres
    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    raw_text = pytesseract.image_to_string(thresh, config=config)
    clean_text = "".join(raw_text.split())

    # Essayer de trouver une plaque conforme
    plate_number = extraire_plaque_valide(clean_text)
    if not plate_number:
        plate_number = clean_text  # en secours

    # Chercher le propriétaire
    owner = "Inconnu"
    if os.path.exists("owners.json"):
        with open("owners.json", "r") as f:
            data = json.load(f)

            # Correspondance exacte
            if plate_number in data:
                owner = data[plate_number]
            else:
                # Correspondance approximative (ex : 1234AB10 ≈ 12354AB10)
                proches = difflib.get_close_matches(plate_number, data.keys(), n=1, cutoff=0.8)
                if proches:
                    plate_number = proches[0]
                    owner = data[plate_number]

    return {"plaque": plate_number, "proprietaire": owner}