from app.main import app
import uvicorn

if __name__ == "__main__":
    # disable reload so the debugger stays attached and breakpoints hit
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)