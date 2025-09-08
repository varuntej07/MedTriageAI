from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import sys
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedTriageAI", 
    description="AI Medical Triage System with Microsoft GraphRAG",
    version="1.0.0"
)

# Simple in-memory state
components_initialized = False
components_error = None

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return JSONResponse({
        "message": "🏥 MedTriageAI with Microsoft GraphRAG is running!",
        "version": "1.0.0",
        "status": "operational",
        "platform": "Vercel",
        "environment_vars": {
            "OPENAI_API_KEY": "✅ Set" if os.getenv("OPENAI_API_KEY", "").replace("your_openai_api_key_here", "") else "❌ Not Set",
            "TWILIO_ACCOUNT_SID": "✅ Set" if os.getenv("TWILIO_ACCOUNT_SID") else "❌ Not Set",
            "TWILIO_AUTH_TOKEN": "✅ Set" if os.getenv("TWILIO_AUTH_TOKEN") else "❌ Not Set"
        },
        "features": {
            "medical_triage": True,
            "voice_calls": True,
            "graphrag": True,
            "emergency_detection": True
        }
    })

@app.get("/health")
async def health_check():
    """Basic health check"""
    global components_initialized, components_error
    
    if not components_initialized:
        try:
            # Try to initialize components
            await initialize_components()
        except Exception as e:
            components_error = str(e)
            logger.error(f"Component initialization failed: {e}")
    
    return JSONResponse({
        "status": "healthy" if components_initialized else "degraded",
        "platform": "Vercel",
        "components_initialized": components_initialized,
        "error": components_error,
        "environment": {
            "python_path": sys.path[:3],  # First 3 paths only
            "current_dir": os.getcwd()
        }
    })

@app.get("/demo/simple")
async def simple_demo():
    """Simple demo that doesn't require complex components"""
    return JSONResponse({
        "demo": "simple_medical_triage",
        "input": "chest pain, sweating",
        "analysis": {
            "urgency": "emergency",
            "recommendation": "Seek immediate emergency medical attention. Call 911.",
            "reasoning": ["Chest pain with sweating indicates possible heart attack"],
            "confidence": 0.9
        },
        "platform": "Vercel",
        "note": "This is a simplified demo. Full system requires component initialization."
    })

async def initialize_components():
    """Try to initialize components with error handling"""
    global components_initialized, components_error
    
    try:
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__
))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Try importing components
        from src.medical_knowledge import MedicalKnowledge
        
        # Simple test initialization
        medical_knowledge = MedicalKnowledge()
        logger.info("✅ Basic components initialized")
        
        components_initialized = True
        components_error = None
        
    except Exception as e:
        components_error = f"Failed to initialize: {str(e)}"
        logger.error(f"Component initialization error: {e}")
        # Don't fail completely - just log the error

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app", 
        host="127.0.0.1",
        port=port, 
        reload=True,
        log_level="info"
    )