# MedTriageAI ??

An AI-powered medical triage system that receives phone calls, analyzes symptoms using Microsoft GraphRAG, and provides explainable medical recommendations.

## ?? Features

- **Phone Integration**: Twilio Voice API for handling phone calls
- **AI Analysis**: Microsoft GraphRAG for medical knowledge reasoning
- **Emergency Detection**: Automatic identification of medical emergencies
- **Conversation Management**: State-driven conversation flow
- **Safety-First**: Always errs on the side of caution with appropriate disclaimers

## ??? Architecture

The system consists of four main components:

### 1. Phone Handler (`src/phone_handler.py`)
- Receives Twilio webhooks
- Converts speech to text and text to speech
- Manages call flow and TwiML responses

### 2. Conversation Manager (`src/conversation_manager.py`)
- Tracks conversation state (greeting ? symptoms ? follow-up ? recommendation)
- Extracts symptoms from natural language
- Manages conversation flow logic

### 3. GraphRAG Engine (`src/graph_rag_engine.py`)
- Microsoft GraphRAG-inspired medical reasoning
- Knowledge graph with medical conditions and relationships
- OpenAI integration for advanced analysis (with fallback)

### 4. Medical Knowledge (`src/medical_knowledge.py`)
- Comprehensive medical condition database
- Emergency trigger detection rules
- Risk stratification and triage logic

## ?? Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Environment Variables**
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_key_here
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
WEAVIATE_URL=http://localhost:8080  # Optional
```

3. **Run the System**
```bash
python main.py
```

The system will start on `http://localhost:8000`

## ?? Testing

Run integration tests to verify all components:
```bash
python test_integration.py
```

## ?? API Endpoints

- `GET /` - System status and information
- `POST /voice/incoming` - Handle incoming Twilio calls  
- `POST /voice/gather` - Process speech input from callers
- `GET /health` - Comprehensive health check
- `GET /demo/test-emergency` - Demo emergency detection
- `GET /demo/test-graphrag` - Demo GraphRAG analysis

## ?? Emergency Detection

The system automatically detects medical emergencies based on:
- **Chest Pain + Additional Symptoms**: Sweating, radiating pain, nausea
- **Stroke Indicators**: Confusion, weakness, speech problems, sudden severe headache
- **Severe Allergic Reactions**: Difficulty breathing, swelling, hives
- **Breathing Difficulties**: Severe shortness of breath, chest pain
- **Mental Health Crises**: Suicidal thoughts or ideation

## ?? Conversation Flow

1. **Greeting**: Welcome and initial symptom gathering
2. **Symptom Collection**: Extract and analyze reported symptoms
3. **Follow-up Questions**: AI-generated targeted questions
4. **Analysis**: GraphRAG-powered medical reasoning
5. **Recommendation**: Clear next steps with explanations

## ?? Safety & Disclaimers

- ?? **Not a Medical Diagnosis**: This system provides triage guidance only
- ?? **Emergency Protocol**: Always directs to 911 for emergencies
- ????? **Professional Care**: Recommends consulting healthcare providers
- ??? **Conservative Approach**: Errs on the side of caution

## ?? Example Usage

### Emergency Scenario
```
Caller: "I'm having severe chest pain and I'm sweating"
System: "?? MEDICAL EMERGENCY DETECTED ?? 
         Call 911 immediately. This could be a heart attack."
```

### Routine Triage
```
Caller: "I have a headache and feel nauseous"
System: "Based on your symptoms, this could be a migraine. 
         I recommend scheduling an appointment with your healthcare provider."
```

## ?? GraphRAG Integration

The system uses a medical knowledge graph with:
- **Nodes**: Medical conditions, symptoms, risk factors
- **Edges**: Relationships between medical entities
- **Reasoning**: Graph traversal for symptom analysis
- **Fallback**: Local analysis when OpenAI is unavailable

## ?? Development Status

? Core medical triage functionality  
? Emergency detection system  
? Twilio voice integration  
? GraphRAG knowledge reasoning  
? Conversation state management  
? Comprehensive testing  

## ?? License

This project is for educational and research purposes. Not intended for production medical use without proper medical oversight and validation.

---
**?? MEDICAL DISCLAIMER**: This system is for informational purposes only and does not constitute medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for proper medical evaluation and care.