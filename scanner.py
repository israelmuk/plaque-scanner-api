import cv2
import pytesseract
import os
import json
import re
import difflib
import numpy as np

def extraire_plaque_valide(text):
    matches = re.findall(r'\b\d{4}[A-Z]{2}\d{2}\b', text)
    return matches[0] if matches else ""

def detect_white_rectangle_with_drapeau(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    white_lower = np.array([0, 0, 150], dtype=np.uint8)
    white_upper = np.array([180, 60, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv, white_lower, white_upper)

    blue_lower = np.array([90, 50, 70])
    blue_upper = np.array([128, 255, 255])
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)

    combined_mask = cv2.bitwise_or(white_mask, blue_mask)

    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    max_area = 0

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.03 * cv2.arcLength(cnt, True), True)
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = w / float(h)

        if len(approx) >= 4 and 2 < aspect_ratio < 7 and w > 100 and h > 30:
            area = w * h
            if area > max_area:
                max_area = area
                best = (x, y, w, h)

    if best:
        x, y, w, h = best
        return image[y:y+h, x:x+w]

    return None

def preprocess_plate_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(blur, 30, 200)

    coords = np.column_stack(np.where(edged > 0))
    if coords.shape[0] > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
    else:
        angle = 0

    (h, w) = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    gray_rotated = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray_rotated, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 25, 15)

    return thresh

def scan_plate(image_path):
    if not os.path.exists(image_path):
        return {"plaque": "", "proprietaire": "Image non trouvée"}

    img = cv2.imread(image_path)
    plate_img = detect_white_rectangle_with_drapeau(img)
    if plate_img is None:
        plate_img = img

    preprocessed = preprocess_plate_image(plate_img)

    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    raw_text = pytesseract.image_to_string(preprocessed, config=config, lang='eng+fra')
    clean_text = "".join(raw_text.split())

    plate_number = extraire_plaque_valide(clean_text) or clean_text

    owner = "Inconnu"
    if os.path.exists("owners.json"):
        with open("owners.json", "r") as f:
            data = json.load(f)
            if plate_number in data:
                owner = data[plate_number]
            else:
                proches = difflib.get_close_matches(plate_number, data.keys(), n=1, cutoff=0.8)
                if proches:
                    plate_number = proches[0]
                    owner = data[plate_number]

    return {"plaque": plate_number, "proprietaire": owner}