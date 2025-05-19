import os
import json
import requests
import difflib

# Clé API Plate Recognizer (à mettre dans les variables d’environnement ou directement ici)
PLATE_RECOGNIZER_TOKEN = os.getenv("PLATE_RECOGNIZER_TOKEN") or "votre_token_plate_recognizer_ici"

def extraire_plaque_valide(text):
    import re
    matches = re.findall(r'\b\d{4}[A-Z]{2}\d{2}\b', text)
    return matches[0] if matches else text.strip()

def get_plate_from_api(image_path):
    try:
        with open(image_path, "rb") as image_file:
            response = requests.post(
                "https://api.platerecognizer.com/v1/plate-reader/",
                files={"upload": image_file},
                headers={"Authorization": f"Token {PLATE_RECOGNIZER_TOKEN}"}
            )
            result = response.json()
            if "results" in result and len(result["results"]) > 0:
                return result["results"][0]["plate"].upper()
            return ""
    except Exception as e:
        print("Erreur Plate Recognizer:", e)
        return ""

def scan_plate(image_path):
    plate_number = get_plate_from_api(image_path)
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