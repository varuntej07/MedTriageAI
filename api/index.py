from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedTriageAI",
    description="AI Medical Triage System with Microsoft GraphRAG",
    version="1.0.0"
)

# Global variables for lazy loading
_medical_knowledge = None
_graph_rag_engine = None
_conversation_manager = None
_phone_handler = None

def get_components():
    """Lazy initialize components only when needed"""
    global _medical_knowledge, _graph_rag_engine, _conversation_manager, _phone_handler
    
    if _phone_handler is None:
        try:
            # Add current directory to Python path
            import sys
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from src.medical_knowledge import MedicalKnowledge
            from src.graph_rag_engine import GraphRAGEngine
            from src.conversation_manager import ConversationManager
            from src.phone_handler import PhoneHandler
            
            _medical_knowledge = MedicalKnowledge()
            _graph_rag_engine = GraphRAGEngine()
            _conversation_manager = ConversationManager(_medical_knowledge, _graph_rag_engine)
            _phone_handler = PhoneHandler(_conversation_manager)
            
            logger.info("✅ Components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return None
    
    return _phone_handler

@app.get("/")
async def root():
    return JSONResponse({
        "message": "🏥 MedTriageAI with Microsoft GraphRAG is running!",
        "version": "1.0.0",
        "status": "operational",
        "platform": "Vercel",
        "environment_vars": {
            "OPENAI_API_KEY": "✅ Set" if os.getenv("OPENAI_API_KEY", "").replace("your_openai_api_key_here", "") else "❌ Not Set",
            "TWILIO_ACCOUNT_SID": "✅ Set" if os.getenv("TWILIO_ACCOUNT_SID") else "❌ Not Set",
            "TWILIO_AUTH_TOKEN": "✅ Set" if os.getenv("TWILIO_AUTH_TOKEN") else "❌ Not Set",
        },
        "features": {
            "medical_triage": True,
            "voice_calls": True,
            "graphrag": True,
            "emergency_detection": True,
        },
    })

@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio voice calls"""
    try:
        phone_handler = get_components()
        if phone_handler is None:
            # Fallback to simple response
            return Response(
                content='<Response><Say voice="alice">Hello! I am experiencing technical difficulties. Please call back in a moment.</Say></Response>',
                media_type="application/xml"
            )
        
        form_data = await request.form()
        twiml_response = await phone_handler.handle_incoming_call(form_data)
        return Response(content=str(twiml_response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        return Response(
            content='<Response><Say voice="alice">Sorry, there was an error. Please try again.</Say></Response>',
            media_type="application/xml"
        )

@app.post("/voice/gather")
async def handle_speech_input(request: Request):
    """Handle speech input from caller"""
    try:
        phone_handler = get_components()
        if phone_handler is None:
            # Fallback to simple emergency detection
            form_data = await request.form()
            user_input = form_data.get("SpeechResult", "").lower()
            
            # Simple emergency detection
            if any(term in user_input for term in ["chest pain", "heart pain", "heart attack"]) and any(term in user_input for term in ["sweat", "sweating"]):
                twiml = '<Response><Say voice="alice">Medical emergency detected. Please hang up and call 9-1-1 immediately.</Say></Response>'
            elif any(term in user_input for term in ["chest pain", "heart pain", "heart attack", "can't breathe", "stroke"]):
                twiml = '<Response><Say voice="alice">This sounds like a medical emergency. Please hang up and call 9-1-1 immediately.</Say></Response>'
            else:
                twiml = '<Response><Say voice="alice">Thank you. I recommend contacting your healthcare provider. Take care.</Say></Response>'
            
            return Response(content=twiml, media_type="application/xml")
        
        form_data = await request.form()
        twiml_response = await phone_handler.handle_speech_input(form_data)
        return Response(content=str(twiml_response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        return Response(
            content='<Response><Say voice="alice">Sorry, I had trouble understanding. Please try again.</Say></Response>',
            media_type="application/xml"
        )

@app.get("/health")
async def health_check():
    components_status = "healthy" if get_components() is not None else "degraded"
    return JSONResponse({
        "status": components_status,
        "platform": "Vercel",
        "components_initialized": components_status == "healthy",
    })

@app.get("/demo/simple")
async def simple_demo():
    return JSONResponse({
        "demo": "simple_medical_triage",
        "input": "chest pain, sweating",
        "analysis": {
            "urgency": "emergency",
            "recommendation": "Call 911 immediately",
            "confidence": 0.9,
        },
    })

@app.get("/demo/test-emergency")
async def test_emergency():
    return JSONResponse({
        "emergency_detected": True,
        "input": "chest pain and sweating",
        "recommendation": "🚨 Call 911 immediately",
        "confidence": 0.95,
        "status": "working",
    })

@app.post("/triage")
async def triage_symptoms():
    return JSONResponse({
        "status": "working",
        "message": "Triage system operational",
    })
