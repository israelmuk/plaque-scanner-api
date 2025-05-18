import cv2
import pytesseract
import os
import json
import re

def scan_plate(image_path):
    if not os.path.exists(image_path):
        return {"plaque": "", "proprietaire": "Image non trouvée"}

    img = cv2.imread(image_path)

    # Conversion en niveaux de gris + amélioration contraste
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)

    # Détection des bords
    edged = cv2.Canny(gray, 30, 200)

    # Détection des contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    plate_img = img  # fallback

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)

        if len(approx) == 4:  # Plaque probable
            x, y, w, h = cv2.boundingRect(c)
            plate_img = gray[y:y+h, x:x+w]
            break

    # OCR sur la plaque détectée
    plate_img = cv2.resize(plate_img, (0, 0), fx=2, fy=2)  # agrandissement
    _, plate_img = cv2.threshold(plate_img, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    raw_text = pytesseract.image_to_string(plate_img, config=config)
    clean_text = "".join(raw_text.split())

    match = re.search(r'\b\d{4}[A-Z]{2}\d{2}\b', clean_text)
    plate_number = match.group(0) if match else clean_text

    # Chercher le propriétaire
    owner = "Inconnu"
    if os.path.exists("owners.json"):
        with open("owners.json", "r") as f:
            data = json.load(f)
            owner = data.get(plate_number, "Inconnu")

    return {"plaque": plate_number, "proprietaire": owner}