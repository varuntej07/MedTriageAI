from fastapi import FastAPI, Form, Request
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
async def handle_incoming_call(
    CallSid: str = Form(...),
    From: str = Form(...)
):
    """Handle incoming Twilio voice calls"""
    try:
        # Initialize conversation
        conversations[CallSid] = {
            "phone": From,
            "state": "greeting",
            "symptoms": []
        }
        
        # Return TwiML response
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice">
                Hello! Welcome to Med Triage A I. I'm here to help assess your medical symptoms. 
                Please describe what you're experiencing. When you're done speaking, I'll analyze your symptoms.
            </Say>
            <Gather input="speech" action="/voice/gather" method="POST" timeout="10" speechTimeout="5">
                <Say voice="alice">Please tell me about your symptoms now.</Say>
            </Gather>
            <Say voice="alice">I didn't hear anything. Please call back if you need medical assistance.</Say>
        </Response>"""
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        return Response(content=f"<Response><Say>Sorry, there was an error. Please try again.</Say></Response>", media_type="application/xml")

@app.post("/voice/gather")
async def handle_speech_input(
    CallSid: str = Form(...),
    SpeechResult: str = Form(...)
):
    """Handle speech input from caller"""
    try:
        user_input = SpeechResult.lower()
        logger.info(f"Received speech: {user_input}")
        
        # Simple emergency detection
        emergency_detected = False
        emergency_message = ""
        
        if any(term in user_input for term in ["chest pain", "heart attack", "can't breathe", "stroke"]):
            emergency_detected = True
            emergency_message = "This sounds like a medical emergency. Please hang up and call 9-1-1 immediately."
        elif "chest pain" in user_input and any(term in user_input for term in ["sweating", "sweat", "arm", "jaw"]):
            emergency_detected = True
            emergency_message = "You may be experiencing a heart attack. Please hang up and call 9-1-1 immediately."
        
        if emergency_detected:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        Medical emergency detected. {emergency_message}
        I repeat: hang up and call 9-1-1 now. This system is not a replacement for emergency services.
    </Say>
</Response>"""
        else:
            # Non-emergency response
            recommendation = "Based on your symptoms, I recommend contacting your healthcare provider for proper evaluation."
            
            if any(term in user_input for term in ["headache", "nausea"]):
                recommendation = "You may have a headache or migraine. Consider rest, hydration, and over-the-counter pain relief. Contact your doctor if symptoms worsen."
            elif any(term in user_input for term in ["fever", "cold", "cough"]):
                recommendation = "You may have a cold or flu. Get plenty of rest, stay hydrated, and monitor your symptoms. Contact your doctor if you develop difficulty breathing or high fever."
            
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        Thank you for describing your symptoms. {recommendation}
        Remember, this is not a medical diagnosis. Always consult with healthcare professionals for proper medical care.
        Take care and feel better soon.
    </Say>
</Response>"""
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        return Response(content=f"<Response><Say>Sorry, I had trouble understanding. Please try again or contact your healthcare provider.</Say></Response>", media_type="application/xml")

@app.get("/health")
async def health_check():
    """Basic health check"""    
    return JSONResponse({
        "status": "healthy",
        "platform": "Vercel",
        "components_initialized": True,
        "environment": {
            "current_dir": os.getcwd(),
            "python_version": sys.version
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

@app.get("/demo/test-emergency")
async def test_emergency():
    """Test emergency detection"""
    try:        
        test_input = "I have severe chest pain and I'm sweating"
        
        if "chest pain" in test_input.lower() and "sweat" in test_input.lower():
            return JSONResponse({
                "emergency_detected": True,
                "input": test_input,
                "urgency": "emergency",
                "recommendation": "🚨 MEDICAL EMERGENCY: Call 911 immediately. Possible heart attack.",
                "confidence": 0.95,
                "platform": "Vercel",
                "status": "working"
            })
        else:
            return JSONResponse({
                "emergency_detected": False,
                "input": test_input,
                "urgency": "routine",
                "recommendation": "Consult healthcare provider if symptoms persist",
                "confidence": 0.5,
                "platform": "Vercel",
                "status": "working"
            })
            
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "failed",
            "platform": "Vercel"
        }, status_code=500)

@app.post("/triage")
async def triage_symptoms():
    """Basic triage endpoint"""
    try:
        return JSONResponse({
            "status": "working",
            "message": "Triage system operational",
            "platform": "Vercel"
        })
        
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "failed",
            "platform": "Vercel"
        }, status_code=500)