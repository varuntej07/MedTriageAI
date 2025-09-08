from fastapi import FastAPI, Request, Form
from fastapi.responses import Response, JSONResponse
import os
import sys
from pathlib import Path
import logging

# Add the project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedTriageAI", 
    description="AI Medical Triage System with Microsoft GraphRAG",
    version="1.0.0"
)

# Global components
medical_knowledge = None
graph_rag_engine = None
conversation_manager = None
phone_handler = None

async def initialize_components():
    """Initialize all components lazily"""
    global medical_knowledge, graph_rag_engine, conversation_manager, phone_handler
    
    if medical_knowledge is None:
        try:
            # Import components
            from src.medical_knowledge import MedicalKnowledge
            from src.graph_rag_engine import GraphRAGEngine
            from src.conversation_manager import ConversationManager
            from src.phone_handler import PhoneHandler
            
            logger.info("🚀 Initializing MedTriageAI components...")
            
            # Initialize in order
            medical_knowledge = MedicalKnowledge()
            logger.info("✅ Medical Knowledge initialized")
            
            graph_rag_engine = GraphRAGEngine()
            logger.info("✅ GraphRAG Engine initialized")
            
            conversation_manager = ConversationManager(medical_knowledge, graph_rag_engine)
            logger.info("✅ Conversation Manager initialized")
            
            phone_handler = PhoneHandler(conversation_manager)
            logger.info("✅ Phone Handler initialized")
            
            logger.info("🎉 All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Component initialization error: {e}")
            logger.info("🔄 Attempting fallback initialization...")
            
            # Fallback initialization
            try:
                from src.medical_knowledge import MedicalKnowledge
                medical_knowledge = MedicalKnowledge()
                logger.info("⚠️ Running with minimal configuration")
            except Exception as fallback_error:
                logger.error(f"❌ Fallback initialization failed: {fallback_error}")

@app.get("/")
async def root():
    """Root endpoint with system status"""
    await initialize_components()
    
    return JSONResponse({
        "message": "🏥 MedTriageAI with Microsoft GraphRAG is running!",
        "version": "1.0.0",
        "status": "operational",
        "platform": "Vercel",
        "features": {
            "medical_triage": True,
            "voice_calls": True,
            "graphrag": True,
            "emergency_detection": True
        },
        "components": {
            "medical_knowledge": medical_knowledge is not None,
            "graph_rag_engine": graph_rag_engine is not None,
            "conversation_manager": conversation_manager is not None,
            "phone_handler": phone_handler is not None
        }
    })

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    await initialize_components()
    
    health_status = {
        "status": "healthy",
        "platform": "Vercel",
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
        
        return JSONResponse(health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e),
            "components": {}
        })

@app.get("/demo/test-emergency")
async def test_emergency():
    """Demo endpoint to test emergency detection"""
    await initialize_components()
    
    if not medical_knowledge:
        return JSONResponse({"error": "Medical knowledge not available"})
    
    try:
        # Simulate emergency scenario
        emergency_symptoms = ["severe chest pain", "sweating", "radiating pain to arm"]
        
        # Check emergency detection
        emergency_result = medical_knowledge.check_emergency_triggers(emergency_symptoms)
        
        return JSONResponse({
            "demo": "emergency_detection",
            "symptoms": emergency_symptoms,
            "emergency_detected": emergency_result is not None,
            "result": emergency_result,
            "platform": "Vercel"
        })
        
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.get("/demo/test-graphrag")
async def test_graphrag():
    """Demo endpoint to test GraphRAG functionality"""
    await initialize_components()
    
    if not graph_rag_engine:
        return JSONResponse({"error": "GraphRAG engine not available"})
    
    try:
        # Test GraphRAG analysis
        test_symptoms = ["headache", "nausea", "light sensitivity"]
        result = await graph_rag_engine.analyze_symptoms(test_symptoms)
        
        return JSONResponse({
            "demo": "graphrag_analysis",
            "input_symptoms": test_symptoms,
            "analysis": result,
            "platform": "Vercel"
        })
        
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio voice calls"""
    await initialize_components()
    
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
    await initialize_components()
    
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

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    )