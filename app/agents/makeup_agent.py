import cv2
import numpy as np
import mediapipe as mp
import json
from app.core.groq_client import run_groq_query


def detect_skin_tone(image_path: str) -> str:
    """
    Estimate user's skin tone (light, medium, dark) using average color.
    """
    image = cv2.imread(image_path)
    if image is None:
        return "unknown"

    # Convert to RGB and normalize
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mean_color = np.mean(image.reshape(-1, 3), axis=0)
    brightness = np.mean(mean_color)

    if brightness > 180:
        return "light"
    elif 120 < brightness <= 180:
        return "medium"
    elif 60 < brightness <= 120:
        return "tan"
    else:
        return "dark"


def detect_skin_type(image_path: str) -> str:
    """
    Roughly classify skin as dry, oily, or normal by analyzing light reflection.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return "unknown"

    # Estimate reflection intensity
    mean_brightness = np.mean(image)
    if mean_brightness > 170:
        return "oily"
    elif mean_brightness < 100:
        return "dry"
    else:
        return "normal"


def suggest_makeup(prompt: str, ref_context: str, image_path: str = None):
    """
    Combines prompt + skin tone/type + stylist cheatsheet → Groq LLM
    for expert-level makeup/chemical application suggestions.
    """
    print("Received image for makeup analysis:", image_path)
    skin_tone, skin_type = "unknown", "unknown"
    if image_path:
        skin_tone = detect_skin_tone(image_path)
        skin_type = detect_skin_type(image_path)

    structured_prompt = f"""
    You are an expert makeup artist and beauty chemist.
    User request: {prompt}
    Detected skin tone: {skin_tone}
    Detected skin type: {skin_type}
    Reference knowledge (from professional cheatsheets): {ref_context}

    Your job:
    1. Suggest a suitable makeup style and product combination.
    2. Include chemical product recommendations (foundation, serum, etc.) with quantity/dilution.
    3. Make it affordable for middle-class customers but high quality.
    4. Respond in Hinglish if user’s input was in Hindi/Hinglish.
    5. Avoid medical or harmful ingredients.

    Return structured JSON with this format:
    {{
      "style": "<look_name>",
      "description": "<why this makeup suits the tone/type>",
      "chemical_instructions": [
        "Use <product> with <amount> ml",
        "Mix <ingredient> ratio 1:<x>"
      ],
      "products": [
        "AffordableProduct1",
        "AffordableProduct2"
      ]
    }}
    """

    response = run_groq_query(structured_prompt)

    try:
        parsed = json.loads(response)
        return parsed
    except Exception:
        # fallback if LLM returns text
        return {
            "style": "Natural Glow Look",
            "description": "Soft natural finish suitable for most tones.",
            "chemical_instructions": [response],
            "products": []
        }
