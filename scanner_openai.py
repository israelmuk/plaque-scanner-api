def get_plate_from_openai(image_path):
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Voici une image d’une voiture. Donne-moi uniquement le numéro de plaque d’immatriculation visible."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ],
            max_tokens=100
        )

        print("Réponse OpenAI :", response["choices"][0]["message"]["content"])
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        print("Erreur OpenAI :", e)
        return None