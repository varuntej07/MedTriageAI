# Minimal Vercel entry point with error handling
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__ + "/../")))

try:
    from main import app
    handler = app
except Exception as e:
    # Fallback minimal FastAPI app if main.py fails
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    fallback_app = FastAPI(title="MedTriageAI Fallback")
    
    @fallback_app.get("/")
    async def fallback_root():
        return JSONResponse({
            "message": "?? MedTriageAI (Minimal Mode)",
            "status": "fallback",
            "error": f"Main app failed to load: {str(e)}",
            "platform": "Vercel"
        })
    
    @fallback_app.get("/health")
    async def fallback_health():
        return JSONResponse({
            "status": "degraded",
            "mode": "fallback",
            "error": f"Components failed to initialize: {str(e)}"
        })
    
    handler = fallback_app