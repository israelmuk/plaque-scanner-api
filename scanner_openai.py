import openai
import base64
import os
import json
import difflib

openai.api_key = os.getenv("OPENAI_API_KEY")  # stocker clé dans variable d'environnement

def extraire_plaque_valide(text):
    import re
    matches = re.findall(r'\b\d{4}[A-Z]{2}\d{2}\b', text)
    return matches[0] if matches else text.strip()

def get_plate_from_openai(image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Voici une image d’une voiture. Donne-moi uniquement le numéro de plaque d’immatriculation visible, sans commentaire."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }
        ],
        max_tokens=100
    )

    raw_text = response["choices"][0]["message"]["content"]
    return extraire_plaque_valide(raw_text)

def scan_plate(image_path):
    plate_number = get_plate_from_openai(image_path)
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