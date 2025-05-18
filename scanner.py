import cv2
import pytesseract
import os
import json

def scan_plate(image_path):
    if not os.path.exists(image_path):
        return {"plaque": "", "proprietaire": "Image non trouvée"}

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    raw_text = pytesseract.image_to_string(thresh, config=config)
    plate_number = "".join(raw_text.split())

    owner = "Inconnu"
    if os.path.exists("owners.json"):
        with open("owners.json", "r") as f:
            data = json.load(f)
            owner = data.get(plate_number, "Inconnu")

    return {"plaque": plate_number, "proprietaire": owner}