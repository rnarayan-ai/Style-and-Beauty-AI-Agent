import os
import cv2
import numpy as np
import mediapipe as mp
from app.core.groq_client import run_groq_query


def analyze_face_shape(image_path: str) -> str:
    """
    Analyze face shape (basic heuristic using Mediapipe landmarks).
    Returns one of: round, oval, square, heart, diamond.
    """
    mp_face_mesh = mp.solutions.face_mesh
    image = cv2.imread(image_path)
    if image is None:
        return "unknown"

    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return "unknown"

        landmarks = results.multi_face_landmarks[0].landmark
        # Calculate key face ratios (rough heuristic)
        forehead_to_chin = abs(landmarks[10].y - landmarks[152].y)
        cheek_width = abs(landmarks[234].x - landmarks[454].x)
        ratio = forehead_to_chin / cheek_width if cheek_width > 0 else 1

        if ratio > 1.4:
            return "oval"
        elif 1.1 < ratio <= 1.4:
            return "round"
        elif 0.9 < ratio <= 1.1:
            return "square"
        else:
            return "diamond"


def suggest_hairstyle(prompt: str, ref_context: str, image_path: str = None):
    """
    Combines face analysis + RAG + user prompt → queries Groq LLM
    for hairstyle suggestions.
    """
    print("Received image for hairstyle analysis:", image_path) 
    face_shape = "unknown"
    if image_path:
        face_shape = analyze_face_shape(image_path)

    combined_prompt_old = f"""
    You are a top-tier virtual hair stylist.
    User description: {prompt}
    Detected face shape: {face_shape}
    Reference data: {ref_context}

    Suggest the **best matching hairstyle** with:
    1. Hairstyle Name
    2. Description (why it suits the face)
    3. Step-by-step barber instructions
    4. Hair product suggestions
    5. Answer in Hinglish if user prompt is in Hindi/Hinglish.

    Respond in structured JSON:
    {{
      "name": "<hairstyle_name>",
      "reason": "<why_it_suits>",
      "instructions": ["step1", "step2", ...],
      "products": ["product1", "product2"]
    }}
    """
    
    combined_prompt = f"""
You are an award-winning AI hair stylist, and professional salon consultant and image designer who understands professional haircutting, face analysis, and beauty aesthetics.

Task:
Generate high-quality, realistic hairstyle **images** that perfectly suit the user's face type.

User details:
- Face shape: {face_shape}
- Face image: [attached or analyzed image input]
- User description or preferences: {prompt}
- Reference database context: {ref_context}

Requirements:
1. Suggest **5 different hairstyles** that are most flattering for an {face_shape} face.
2. Each hairstyle should be shown as a **realistic AI-generated image** (photo-real style, front view, natural lighting).
3. Include **name, reasoning, and style notes** for each hairstyle.
4. Focus on *balance, proportion, and framing* for the given face shape.
5. Use natural hair texture unless user specifies otherwise.
6. Match hair color tone to user complexion.
7. Avoid cartoon or unrealistic rendering — output should look like a professional salon catalog photo.

Output format (structured JSON + image prompt guide):
{
  "hairstyles": [
    {
      "name": "<hairstyle_name>",
      "reason": "<why_it_suits_the_face>",
      "visual_prompt": "A detailed image generation description for this hairstyle",
      "image_style": "photo-realistic, studio lighting, clean background",
      "camera_angle": "frontal portrait",
      "products": ["<styling_product1>", "<styling_product2>"]
    },
    ...
  ]
}

If the user input is in Hindi or Hinglish, write explanations in Hinglish but keep technical and JSON parts in English.
"""


    response = run_groq_query(combined_prompt)

    # --- Basic sanitization ---
    try:
        import json
        parsed = json.loads(response)
        return parsed
    except Exception:
        # fallback if model returns plain text
        return {
            "name": "Custom Style Suggestion",
            "reason": "Based on AI analysis and stylistic trends.",
            "instructions": [response],
            "products": []
        }
