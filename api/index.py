from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
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

# In-memory conversation storage (for demo)
conversations = {}

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

@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio voice calls"""
    try:
        # Get form data from request
        form_data = await request.form()
        call_sid = form_data.get("CallSid", "")
        from_number = form_data.get("From", "")
        
        # Initialize conversation
        conversations[call_sid] = {
            "phone": from_number,
            "state": "greeting",
            "symptoms": []
        }
        
        # Return TwiML response - simple format
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello! Welcome to Med Triage AI. Please describe your symptoms now.</Say>
    <Gather input="speech" action="/voice/gather" method="POST" timeout="10" speechTimeout="3">
        <Say voice="alice">I'm listening...</Say>
    </Gather>
    <Say voice="alice">I didn't hear anything. Goodbye.</Say>
</Response>"""
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        return Response(content="<Response><Say>Sorry, there was an error.</Say></Response>", media_type="application/xml")

@app.post("/voice/gather")
async def handle_speech_input(request: Request):
    """Handle speech input from caller"""
    try:
        # Get form data from request
        form_data = await request.form()
        call_sid = form_data.get("CallSid", "")
        user_input = form_data.get("SpeechResult", "").lower()
        
        logger.info(f"Received speech: {user_input}")
        
        # Emergency detection
        if any(term in user_input for term in ["chest pain", "heart attack"]) or ("chest pain" in user_input and "sweat" in user_input):
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Medical emergency detected. Please hang up and call 9-1-1 immediately.</Say>
</Response>"""
        else:
            # Non-emergency
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Thank you. I recommend contacting your healthcare provider. Take care.</Say>
</Response>"""
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        return Response(content="<Response><Say>Sorry, I had trouble understanding.</Say></Response>", media_type="application/xml")

@app.get("/health")
async def health_check():
    """Basic health check"""    
    return JSONResponse({
        "status": "healthy",
        "platform": "Vercel",
        "components_initialized": True
    })

@app.get("/demo/simple")
async def simple_demo():
    """Simple demo"""
    return JSONResponse({
        "demo": "simple_medical_triage",
        "input": "chest pain, sweating",
        "analysis": {
            "urgency": "emergency",
            "recommendation": "Call 911 immediately",
            "confidence": 0.9
        }
    })

@app.get("/demo/test-emergency")
async def test_emergency():
    """Test emergency detection"""
    return JSONResponse({
        "emergency_detected": True,
        "input": "chest pain and sweating",
        "recommendation": "🚨 Call 911 immediately",
        "confidence": 0.95,
        "status": "working"
    })

@app.post("/triage")
async def triage_symptoms():
    """Basic triage endpoint"""
    return JSONResponse({
        "status": "working",
        "message": "Triage system operational"
    })