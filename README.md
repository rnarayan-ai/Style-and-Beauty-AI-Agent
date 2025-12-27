# 💄 AI Beauty Stylist
> **Transforming Personal Style through Market Intelligence & Generative AI**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![Groq](https://img.shields.io/badge/LLM-Groq_Inference-f55036?style=for-the-badge)](https://groq.com/)
[![SDXL](https://img.shields.io/badge/GenAI-SDXL_1.0-blueviolet?style=for-the-badge)](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)

## 🌟 Project Overview
An interactive AI assistant for beauty and style that accepts text, voice, and images. The system performs advanced vision analysis to suggest makeup and hairstyles tailored to the user's specific facial structure and attributes.

* **Backend:** FastAPI performing vision analysis and LLM orchestration.
* **Frontend:** React + Vite providing a sleek chat UI with camera and voice support.

---

## 🛠️ Tech Stack

### **Backend (Python 3.10+)**
* **Web Framework:** FastAPI & Uvicorn
* **Vision & Attributes:** DeepFace, MediaPipe, OpenCV
* **Vector Database:** ChromaDB (for knowledge retrieval)
* **Generative AI:** Stable Diffusion XL (diffusers) & LCM-LoRA for speed
* **Identity Preservation:** IP-Adapter & ControlNet
* **LLM Runtime:** Groq API (Llama3/Mixtral)
* **Audio (ASR):** OpenAI Whisper

### **Frontend (React)**
* **Build Tool:** Vite
* **UI Components:** Custom React components for Chat, Camera, and Voice
* **Communication:** Fetch API with backend proxying

---

## 🏗️ Architecture & Structure

### **Key Backend Modules**
* `app/main.py`: Main API entry point and route registration.
* `app/core/groq_client.py`: Wrapper for Groq LLM queries.
* `app/utils/sd_generate.py`: SDXL generation logic with LCM acceleration.
* `app/agents/`: Domain-specific agents for makeup and hairstyle parsing.

### **Key Frontend Modules**
* `frontend/src/components/`: Chatbot, Camera, and Message UI.
* `frontend/src/utils/`: API handlers and prompt builders.

---

## 🔄 Prompting & Data Flow

1.  **Analyze:** User uploads an image to `/api/analyze`.
2.  **Vision Data:** Backend returns structured JSON (face shape, skin tone, current hair).
3.  **Prompt Build:** Frontend uses `promptBuilder.js` to create a context-aware LLM prompt.
4.  **LLM Query:** `/api/message` proxies the request to Groq for expert advice.
5.  **Render:** The response is cleaned, sanitized, and displayed as HTML in the chat.

---

## 🚀 Setup & Installation

### **1. Backend Setup**
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt

# Start the application
python run.py


# Environment Variables (.env)
Create a .env file in the root directory:
GROQ_API_KEY: Your Groq API key.
HUGGINGFACE_HUB_TOKEN: Required for downloading gated SDXL models.
REDIS_HOST / REDIS_PORT: (Optional) For caching.


⚠️ Important Implementation Notes
GPU vs CPU: This project is optimized for GPU. Using a CPU for Stable Diffusion or Whisper will be significantly slower.
Security: Always sanitize HTML returned by the LLM before rendering using dangerouslySetInnerHTML.
FFMPEG: Ensure ffmpeg is installed on your system PATH for audio/voice features to work.

📜 License & Credits
Models: Respect the licenses of Hugging Face, DeepFace, and MediaPipe.
Terms: This is a functional prototype. Adapt licensing and commercial terms before production use.
