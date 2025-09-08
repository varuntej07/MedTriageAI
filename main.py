from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
import os
from dotenv import load_dotenv
import uvicorn
import logging

from src.phone_handler import PhoneHandler
from src.conversation_manager import ConversationManager
from src.graph_rag_engine import GraphRAGEngine
from src.medical_knowledge import MedicalKnowledge

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedTriageAI", 
    description="AI Medical Triage System with Microsoft GraphRAG",
    version="1.0.0"
)

# Initialize components with proper error handling
medical_knowledge = None
graph_rag_engine = None
conversation_manager = None
phone_handler = None

@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup"""
    global medical_knowledge, graph_rag_engine, conversation_manager, phone_handler
    
    try:
        logger.info("?? Starting MedTriageAI with GraphRAG...")
        
        # Check for required environment variables
        missing_vars = []
        if not os.getenv("OPENAI_API_KEY"):
            missing_vars.append("OPENAI_API_KEY")
        if not os.getenv("TWILIO_ACCOUNT_SID"):
            missing_vars.append("TWILIO_ACCOUNT_SID")
        if not os.getenv("TWILIO_AUTH_TOKEN"):
            missing_vars.append("TWILIO_AUTH_TOKEN")
        
        if missing_vars:
            logger.warning(f"??  Missing environment variables: {', '.join(missing_vars)}")
            logger.warning("Some features may be limited. Please check your .env file.")
        
        # Initialize components
        medical_knowledge = MedicalKnowledge()
        logger.info("? Medical Knowledge initialized")
        
        graph_rag_engine = GraphRAGEngine()
        logger.info("? GraphRAG Engine initialized")
        
        conversation_manager = ConversationManager(medical_knowledge, graph_rag_engine)
        logger.info("? Conversation Manager initialized")
        
        phone_handler = PhoneHandler(conversation_manager)
        logger.info("? Phone Handler initialized")
        
        logger.info("?? MedTriageAI startup complete!")
        
    except Exception as e:
        logger.error(f"? Startup error: {e}")
        # Don't fail startup completely - create minimal components
        medical_knowledge = MedicalKnowledge()
        graph_rag_engine = GraphRAGEngine()
        conversation_manager = ConversationManager(medical_knowledge, graph_rag_engine)
        phone_handler = PhoneHandler(conversation_manager)
        logger.warning("??  Started with minimal configuration")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        if graph_rag_engine:
            await graph_rag_engine.shutdown()
        logger.info("? Shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "?? MedTriageAI with Microsoft GraphRAG is running!",
        "version": "1.0.0",
        "status": "operational",
        "features": {
            "medical_triage": True,
            "voice_calls": True,
            "graphrag": True,
            "emergency_detection": True
        }
    }

@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio voice calls"""
    if not phone_handler:
        return Response(
            content="System not ready", 
            status_code=503,
            media_type="text/plain"
        )
    
    try:
        form_data = await request.form()
        return await phone_handler.handle_incoming_call(form_data)
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        return Response(
            content="Internal server error",
            status_code=500,
            media_type="text/plain"
        )

@app.post("/voice/gather")
async def handle_speech_input(request: Request):
    """Handle speech input from caller"""
    if not phone_handler:
        return Response(
            content="System not ready",
            status_code=503,
            media_type="text/plain"
        )
    
    try:
        form_data = await request.form()
        return await phone_handler.handle_speech_input(form_data)
    except Exception as e:
        logger.error(f"Error handling speech input: {e}")
        return Response(
            content="Internal server error",
            status_code=500,
            media_type="text/plain"
        )

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "components": {}
    }
    
    try:
        # Check medical knowledge
        if medical_knowledge:
            conditions_count = len(medical_knowledge.conditions)
            health_status["components"]["medical_knowledge"] = {
                "status": "healthy",
                "conditions_loaded": conditions_count
            }
        else:
            health_status["components"]["medical_knowledge"] = {"status": "unavailable"}
        
        # Check GraphRAG engine
        if graph_rag_engine:
            graph_nodes = len(graph_rag_engine.medical_graph.nodes) if graph_rag_engine.medical_graph else 0
            health_status["components"]["graphrag_engine"] = {
                "status": "healthy",
                "knowledge_graph_nodes": graph_nodes,
                "weaviate_connected": graph_rag_engine.weaviate_client is not None
            }
        else:
            health_status["components"]["graphrag_engine"] = {"status": "unavailable"}
        
        # Check conversation manager
        health_status["components"]["conversation_manager"] = {
            "status": "healthy" if conversation_manager else "unavailable",
            "active_conversations": len(conversation_manager.conversations) if conversation_manager else 0
        }
        
        # Check phone handler
        health_status["components"]["phone_handler"] = {
            "status": "healthy" if phone_handler else "unavailable"
        }
        
        # Overall status
        all_healthy = all(
            comp.get("status") == "healthy" 
            for comp in health_status["components"].values()
        )
        health_status["status"] = "healthy" if all_healthy else "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "components": {}
        }

@app.get("/demo/test-emergency")
async def test_emergency():
    """Demo endpoint to test emergency detection"""
    if not conversation_manager:
        return {"error": "System not ready"}
    
    try:
        # Simulate emergency scenario
        emergency_symptoms = ["severe chest pain", "sweating", "radiating pain to arm"]
        
        # Check emergency detection
        emergency_result = medical_knowledge.check_emergency_triggers(emergency_symptoms)
        
        return {
            "demo": "emergency_detection",
            "symptoms": emergency_symptoms,
            "emergency_detected": emergency_result is not None,
            "result": emergency_result
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/demo/test-graphrag")
async def test_graphrag():
    """Demo endpoint to test GraphRAG functionality"""
    if not graph_rag_engine:
        return {"error": "GraphRAG engine not available"}
    
    try:
        # Test GraphRAG analysis
        test_symptoms = ["headache", "nausea", "light sensitivity"]
        result = await graph_rag_engine.analyze_symptoms(test_symptoms)
        
        return {
            "demo": "graphrag_analysis",
            "input_symptoms": test_symptoms,
            "analysis": result
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    )