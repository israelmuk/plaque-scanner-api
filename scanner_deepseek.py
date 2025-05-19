import requests
import os
import json
import difflib
import base64

# Clé HuggingFace ou URL API du modèle
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-Vision"
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN") or "votre_token_huggingface_ici"

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
    "Content-Type": "application/json"
}

def extraire_plaque_valide(text):
    import re
    matches = re.findall(r'\b\d{4}[A-Z]{2}\d{2}\b', text)
    return matches[0] if matches else text.strip()

def get_plate_from_deepseek(image_path):
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        data = {
            "inputs": {
                "image": image_b64,
                "prompt": "Voici une image d'une voiture. Peux-tu me dire quel est le numéro exact visible sur la plaque d'immatriculation ?"
            }
        }
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=data)
        result = response.json()

        if isinstance(result, dict) and "generated_text" in result:
            return extraire_plaque_valide(result["generated_text"])
        elif isinstance(result, list) and "generated_text" in result[0]:
            return extraire_plaque_valide(result[0]["generated_text"])
        else:
            print("Réponse inattendue :", result)
            return "Inconnu"
    except Exception as e:
        print("Erreur DeepSeek HuggingFace :", e)
        return "ErreurDeepSeek"

def scan_plate(image_path):
    plate_number = get_plate_from_deepseek(image_path)
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