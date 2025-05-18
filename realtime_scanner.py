import cv2
import pytesseract
import json

# Définir le chemin de Tesseract si nécessaire
# Exemple Windows : pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Charger la base des propriétaires
with open("owners.json", "r") as f:
    owners = json.load(f)

# Ouvrir la webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    raw_text = pytesseract.image_to_string(thresh, config=config)
    plate = "".join(raw_text.split())

    owner = owners.get(plate, "Inconnu") if plate else "Inconnu"

    label = f"{plate} - {owner}" if plate else "Aucune plaque détectée"
    cv2.putText(frame, label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Scanner de Plaque", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()