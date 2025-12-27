# AI Beauty Stylist — README

This README summarizes the implementation, tools, and functions used to build the AI market-intelligence / beauty-stylist application (backend + frontend). It documents tech stack, core modules/endpoints, model & runtime requirements, setup and run instructions, and important notes.marizes the implementation, tools, and functions used to build the AI market-intelligence / beauty-stylist application (backend + frontend). It documents tech stack, core modules/endpoints, model & runtime requirements, setup and run instructions, and important notes.

---

## Project overview
An interactive AI assistant for beauty & style that accepts text, voice and images (upload or camera). Backend (FastAPI/Python) performs vision analysis, makeup/hairstyle suggestions, and LLM prompting (Groq). Frontend (React + Vite) provides a chat UI, image/camera upload, and voice recording. voice and images (upload or camera). Backend (FastAPI/Python) performs vision analysis, makeup/hairstyle suggestions, and LLM prompting (Groq). Frontend (React + Vite) provides a chat UI, image/camera upload, and voice recording.

---

## Architecture (high level)
- Frontend (React + Vite)
  - Chat UI, file/camera capture, voice recording
  - Calls backend endpoints under `/api/*`kend endpoints under `/api/*`
- Backend (FastAPI)tAPI)
  - Vision & attribute analysis (DeepFace, MediaPipe, OpenCV)
  - Vector/knowledge ingestion (Chroma / chromadb)roma / chromadb)
  - LLM orchestration (run_groq_query)uery)
  - Stable Diffusion XL image generation utility (diffusers)lity (diffusers)
  - ASR support (whisper) for audio input
  - Redis for caching/session state
- Model/data storage: local / persistent Chromadb directory, Redis


































































































































































































- or produce a minimal `requirements.txt` and `package.json` matching the exact packages in your codebase.- generate a ready-to-save `README.md` file in the repo root,If you want, I can:---- This project is a functional prototype — adapt licensing & commercial terms before production use.- Uses multiple open-source models & libraries. Respect each model's license (Hugging Face model licenses, diffusers, DeepFace, MediaPipe, chromadb).## License & credits---- Frontend: frontend/src/components/Chatbot.jsx, Chat.jsx, Message.jsx, frontend/src/utils/{api.js,parseAnalysis.js,promptBuilder.js}- Backend: app/main.py, app/core/groq_client.py, app/core.py, app/utils/sd_generate.py, app/utils/asr.py, app/routes/message.py, app/routes/analyze.py, app/agents/*## Files of interest---- Keep secrets out of VCS (use .env or secret store).- Rate-limit and authenticate LLM endpoints; sanitize inputs for user content.- Use model-specific installation for torch to match CUDA version.- GPU recommended for Stable Diffusion and torch; CPU is very slow.- Do not enable `--reload` with the VS Code debugger (reload spawns child processes).- Validate & sanitize any HTML returned by LLM before rendering client-side. Frontend currently converts simple markdown to HTML and uses `dangerouslySetInnerHTML` — sanitize in production.## Important implementation notes & best practices---  ```    -F "text=Analyze makeup and hairstyle"    -F "image=@/path/photo.jpg" \  curl -X POST http://localhost:8000/api/analyze \  ```bash- Call analyze:  ```    -d '{"prompt":"Hello, give me a makeup tip for a diamond face shape."}'    -H "Content-Type: application/json" \  curl -X POST http://localhost:8000/api/message \  ```bash- Call LLM route:## Example HTTP usage---  ```  }    ]      }        "justMyCode": false        "env": { "PYTHONPATH": "${workspaceFolder}" },        "cwd": "${workspaceFolder}",        "console": "integratedTerminal",        "program": "${workspaceFolder}/run.py",        "request": "launch",        "type": "python",        "name": "Python: Run run.py (FastAPI)",      {    "configurations": [    "version": "0.2.0",  {  ```json- Create `.vscode/launch.json`:- Add run.py that starts uvicorn without `--reload` (so breakpoints hit).## VS Code debugging---- Ensure .env or system env are set and not committed to version control.- CHROMA_DIR or CHROMA_PERSIST_DIR — chroma DB path- REDIS_HOST / REDIS_PORT — redis config- GROQ_API_KEY or similar — credentials for Groq integration- HUGGINGFACE_HUB_TOKEN — required to download SDXL if model is gated## Environment variables & secrets---   - Vite runs on http://localhost:5173 (proxy configured for `/api` → backend).     ```     npm run dev     npm install     cd frontend     ```powershell   - From frontend folder:3. Frontend     ```     python run.py     # or for debugging (no reload)     python -m uvicorn app.main:app --reload     cd "D:\AI Beauty Stylist Makeup Guide"     ```powershell   - Run backend:     - If using diffusers SDXL, set HUGGINGFACE_HUB_TOKEN     - ffmpeg must be installed and on PATH (choco / winget or download builds)   - Install model deps:     If installing torch manually, use official selector (https://pytorch.org/get-started/locally/).     ```     pip install -r requirements.txt     python -m pip install --upgrade pip     ```powershell   - Install dependencies (example):     ```     .\.venv\Scripts\Activate.ps1     python -m venv .venv     ```powershell   - Create & activate venv:2. Python backend1. Clone repo and open project root.## Setup & run (development)---6. Backend performs `run_groq_query(combined_prompt)` and returns the formatted response. Frontend renders the response as HTML (bold/italic and paragraphs).5. Frontend calls `/api/message` with the prompt (and optional context).4. Frontend builds a targeted LLM prompt via `buildMakeupStyleReview()` that includes the parsed data and raw JSON.3. Frontend runs `extractFromAnalysis()` to get face_shape, hairstyle list, makeup style, etc.2. Backend returns structured JSON with hairstyles, makeup, notes.1. Frontend uploads image + prompt to `/api/analyze`.## Prompting flow (how data is used)---    - index.css — UI styles      - promptBuilder.js — `buildMakeupStyleReview(parsed, rawData)`      - parseAnalysis.js — `extractFromAnalysis(data)`      - api.js — `sendAnalyze`, `callGroqMessage`    - utils/      - Message.jsx — renders text / html / image / audio messages (supports dangerouslySetInnerHTML for bot HTML)      - Chat.jsx / Chatbot.jsx — chat controls, camera, recording    - components/    - App.jsx or Chatbot.jsx — main chat container  - src/  - package.json, vite.config.js  - index.html- frontend/## Frontend structure & key files---  - image/audio analyze endpoint- app/routes/analyze.py (or similar)  - ingestion endpoints for adding knowledge (PDFs/text → Chroma)- app/routes/ingest.py  - router to handle `/api/message` (Groq proxy)- app/routes/message.py  - hairstyle_agent.py, makeup.py — domain agents to parse attributes, create combined prompts, call LLM and produce structured suggestions- app/agents/*  - ASR wrapper (whisper)- app/utils/asr.py  - generate_sdxl_images(prompt, out_dir, num_images=...) — uses diffusers StableDiffusionXLPipeline- app/utils/sd_generate.py  - LLM client wrapper: `run_groq_query(prompt)` (synchronous wrapper used by route)- app/core/groq_client.py  - chroma_client initialization (PersistentClient)- app/core.py  - helper: `run_groq_query` via `app.core.groq_client`  - `/api/message` — receives a prompt, calls `run_groq_query(combined_prompt)` and returns LLM result  - `/api/analyze` — receive image + prompt (Form/File); runs vision analysis & returns structured JSON  - FastAPI app, CORS, route registration- app/main.py## Key backend modules & routes---- Optional: Chocolatey / winget for OS-level installs (ffmpeg)  - VS Code (debugging & launch.json)  - Git (recommended)  - ffmpeg (required by whisper & some pipelines)  - Node.js / npm (or yarn / pnpm)- Tools:  - Fetch API for HTTP  - @vitejs/plugin-react  - Vite  - React (18)- Frontend:  - python-dotenv  - whisper / openai-whisper (ASR)  - torch (CUDA/CPU)  - diffusers, transformers, accelerate, safetensors (Stable Diffusion XL)  - MediaPipe (face landmarks)  - DeepFace (face attribute extraction)  - OpenCV (cv2), NumPy  - groq client integration (LLM runtime)  - redis (redis-py)  - chromadb (Chroma vector DB)  - Pydantic (settings/models)  - Uvicorn (ASGI server)  - FastAPI (web API)- Backend frameworks & libs:- Languages: Python 3.10+ (backend), JavaScript/React (frontend)## Tech stack---- Dev tooling: uvicorn, VS Code debug configs- Dev tooling: uvicorn, VS Code debug configs

---

## Tech stack
- Languages: Python 3.10+ (backend), JavaScript/React (frontend)
- Backend frameworks & libs:
  - FastAPI (web API)
  - Uvicorn (ASGI server)
  - Pydantic (settings/models)
  - chromadb (Chroma vector DB)
  - redis (redis-py)
  - groq client integration (LLM runtime)
  - OpenCV (cv2), NumPy
  - DeepFace (face attribute extraction)
  - MediaPipe (face landmarks)
  - diffusers, transformers, accelerate, safetensors (Stable Diffusion XL)
  - torch (CUDA/CPU)
  - whisper / openai-whisper (ASR)
  - python-dotenv
- Frontend:
  - React (18)
  - Vite
  - @vitejs/plugin-react
  - Fetch API for HTTP
- Tools:
  - Node.js / npm (or yarn / pnpm)
  - ffmpeg (required by whisper & some pipelines)
  - Git (recommended)
  - VS Code (debugging & launch.json)
- Optional: Chocolatey / winget for OS-level installs (ffmpeg)

---

## Key backend modules & routes
- app/main.py
  - FastAPI app, CORS, route registration
  - `/api/analyze` — receive image + prompt (Form/File); runs vision analysis & returns structured JSON
  - `/api/message` — receives a prompt, calls `run_groq_query(combined_prompt)` and returns LLM result
  - helper: `run_groq_query` via `app.core.groq_client`
- app/core.py
  - chroma_client initialization (PersistentClient)
- app/core/groq_client.py
  - LLM client wrapper: `run_groq_query(prompt)` (synchronous wrapper used by route)
- app/utils/sd_generate.py
  - generate_sdxl_images(prompt, out_dir, num_images=...) — uses diffusers StableDiffusionXLPipeline
- app/utils/asr.py
  - ASR wrapper (whisper)
- app/agents/*
  - hairstyle_agent.py, makeup.py — domain agents to parse attributes, create combined prompts, call LLM and produce structured suggestions
- app/routes/message.py
  - router to handle `/api/message` (Groq proxy)
- app/routes/ingest.py
  - ingestion endpoints for adding knowledge (PDFs/text → Chroma)
- app/routes/analyze.py (or similar)
  - image/audio analyze endpoint

---

## Frontend structure & key files
- frontend/
  - index.html
  - package.json, vite.config.js
  - src/
    - App.jsx or Chatbot.jsx — main chat container
    - components/
      - Chat.jsx / Chatbot.jsx — chat controls, camera, recording
      - Message.jsx — renders text / html / image / audio messages (supports dangerouslySetInnerHTML for bot HTML)
    - utils/
      - api.js — `sendAnalyze`, `callGroqMessage`
      - parseAnalysis.js — `extractFromAnalysis(data)`
      - promptBuilder.js — `buildMakeupStyleReview(parsed, rawData)`
    - index.css — UI styles

---

## Prompting flow (how data is used)
1. Frontend uploads image + prompt to `/api/analyze`.
2. Backend returns structured JSON with hairstyles, makeup, notes.
3. Frontend runs `extractFromAnalysis()` to get face_shape, hairstyle list, makeup style, etc.
4. Frontend builds a targeted LLM prompt via `buildMakeupStyleReview()` that includes the parsed data and raw JSON.
5. Frontend calls `/api/message` with the prompt (and optional context).
6. Backend performs `run_groq_query(combined_prompt)` and returns the formatted response. Frontend renders the response as HTML (bold/italic and paragraphs).

---

## Setup & run (development)
1. Clone repo and open project root.
2. Python backend
   - Create & activate venv:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - Install dependencies (example):
     ```powershell
     python -m pip install --upgrade pip
     pip install -r requirements.txt
     ```
     If installing torch manually, use official selector (https://pytorch.org/get-started/locally/).
   - Install model deps:
     - ffmpeg must be installed and on PATH (choco / winget or download builds)
     - If using diffusers SDXL, set HUGGINGFACE_HUB_TOKEN
   - Run backend:
     ```powershell
     cd "D:\AI Beauty Stylist Makeup Guide"
     python -m uvicorn app.main:app --reload
     # or for debugging (no reload)
     python run.py
     ```
3. Frontend
   - From frontend folder:
     ```powershell
     cd frontend
     npm install
     npm run dev
     ```
   - Vite runs on http://localhost:5173 (proxy configured for `/api` → backend).

---

## Environment variables & secrets
- HUGGINGFACE_HUB_TOKEN — required to download SDXL if model is gated
- GROQ_API_KEY or similar — credentials for Groq integration
- REDIS_HOST / REDIS_PORT — redis config
- CHROMA_DIR or CHROMA_PERSIST_DIR — chroma DB path
- Ensure .env or system env are set and not committed to version control.

---

## VS Code debugging
- Add run.py that starts uvicorn without `--reload` (so breakpoints hit).
- Create `.vscode/launch.json`:
  ```json
  {
    "version": "0.2.0",
    "configurations": [
      {
        "name": "Python: Run run.py (FastAPI)",
        "type": "python",
        "request": "launch",
        "program": "${workspaceFolder}/run.py",
        "console": "integratedTerminal",
        "cwd": "${workspaceFolder}",
        "env": { "PYTHONPATH": "${workspaceFolder}" },
        "justMyCode": false
      }
    ]
  }
  ```

---

## Example HTTP usage
- Call LLM route:
  ```bash
  curl -X POST http://localhost:8000/api/message \
    -H "Content-Type: application/json" \
    -d '{"prompt":"Hello, give me a makeup tip for a diamond face shape."}'
  ```
- Call analyze:
  ```bash
  curl -X POST http://localhost:8000/api/analyze \
    -F "image=@/path/photo.jpg" \
    -F "text=Analyze makeup and hairstyle"
  ```

---

## Important implementation notes & best practices
- Validate & sanitize any HTML returned by LLM before rendering client-side. Frontend currently converts simple markdown to HTML and uses `dangerouslySetInnerHTML` — sanitize in production.
- Do not enable `--reload` with the VS Code debugger (reload spawns child processes).
- GPU recommended for Stable Diffusion and torch; CPU is very slow.
- Use model-specific installation for torch to match CUDA version.
- Rate-limit and authenticate LLM endpoints; sanitize inputs for user content.
- Keep secrets out of VCS (use .env or secret store).

---

## Files of interest
- Backend: app/main.py, app/core/groq_client.py, app/core.py, app/utils/sd_generate.py, app/utils/asr.py, app/routes/message.py, app/routes/analyze.py, app/agents/*
- Frontend: frontend/src/components/Chatbot.jsx, Chat.jsx, Message.jsx, frontend/src/utils/{api.js,parseAnalysis.js,promptBuilder.js}

---

## License & credits
- Uses multiple open-source models & libraries. Respect each model's license (Hugging Face model licenses, diffusers, DeepFace, MediaPipe, chromadb).
- This project is a functional prototype — adapt licensing & commercial terms before production use.

---
