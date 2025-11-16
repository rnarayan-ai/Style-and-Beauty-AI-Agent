import cv2
import numpy as np
from typing import Dict


async def analyze_image(path: str) -> Dict[str, str]:
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    face_shape = "oval"
    hair_texture = "straight"
    skin_tone = "medium"
    return {"face_shape": face_shape, "hair_texture": hair_texture, "skin_tone": skin_tone}