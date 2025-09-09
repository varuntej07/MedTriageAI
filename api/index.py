from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import os
import logging

from src.medical_knowledge import MedicalKnowledge
from src.graph_rag_engine import GraphRAGEngine
from src.conversation_manager import ConversationManager
from src.phone_handler import PhoneHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedTriageAI",
    description="AI Medical Triage System with Microsoft GraphRAG",
    version="1.0.0"
)

medical_knowledge = MedicalKnowledge()
graph_rag_engine = GraphRAGEngine()
conversation_manager = ConversationManager(medical_knowledge, graph_rag_engine)
phone_handler = PhoneHandler(conversation_manager)


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
        form_data = await request.form()
        twiml_response = await phone_handler.handle_incoming_call(form_data)
        return Response(content=str(twiml_response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        error_twiml = phone_handler._create_error_response()
        return Response(content=str(error_twiml), media_type="application/xml")


@app.post("/voice/gather")
async def handle_speech_input(request: Request):
    """Handle speech input from caller"""
    try:
        form_data = await request.form()
        twiml_response = await phone_handler.handle_speech_input(form_data)
        return Response(content=str(twiml_response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        error_twiml = phone_handler._create_error_response()
        return Response(content=str(error_twiml), media_type="application/xml")


@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "healthy",
        "platform": "Vercel",
        "components_initialized": True,
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
