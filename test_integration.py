#!/usr/bin/env python3
"""
Integration test for MedTriageAI system components
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.medical_knowledge import MedicalKnowledge
from src.graph_rag_engine import GraphRAGEngine  
from src.conversation_manager import ConversationManager
from src.phone_handler import PhoneHandler

async def test_medical_knowledge():
    """Test medical knowledge base"""
    print("?? Testing Medical Knowledge...")
    
    mk = MedicalKnowledge()
    
    # Test emergency detection
    emergency_symptoms = ["severe chest pain", "sweating", "radiating pain to arm"]
    emergency_result = mk.check_emergency_triggers(emergency_symptoms)
    
    print(f"? Emergency Detection Test:")
    print(f"   Symptoms: {emergency_symptoms}")
    print(f"   Emergency Detected: {emergency_result is not None}")
    if emergency_result:
        print(f"   Action: {emergency_result['action']}")
    
    # Test condition matching
    routine_symptoms = ["headache", "nausea", "light sensitivity"]
    matches = mk.get_condition_by_symptoms(routine_symptoms)
    
    print(f"? Condition Matching Test:")
    print(f"   Symptoms: {routine_symptoms}")
    print(f"   Top Match: {matches[0]['condition']['name'] if matches else 'None'}")
    print()

async def test_graph_rag_engine():
    """Test GraphRAG engine"""
    print("?? Testing GraphRAG Engine...")
    
    engine = GraphRAGEngine()
    
    # Test symptom analysis
    test_symptoms = ["headache", "nausea", "light sensitivity"]
    result = await engine.analyze_symptoms(test_symptoms)
    
    print(f"? GraphRAG Analysis Test:")
    print(f"   Symptoms: {test_symptoms}")
    print(f"   Urgency: {result.get('urgency', 'unknown')}")
    print(f"   Confidence: {result.get('confidence', 0):.1%}")
    print(f"   Method: {result.get('analysis_method', 'unknown')}")
    
    # Test follow-up questions
    questions = await engine.generate_follow_up_questions(test_symptoms)
    print(f"   Follow-up Questions: {len(questions)} generated")
    for i, q in enumerate(questions[:2], 1):
        print(f"     {i}. {q}")
    print()
    
    await engine.shutdown()

async def test_conversation_manager():
    """Test conversation manager"""
    print("?? Testing Conversation Manager...")
    
    mk = MedicalKnowledge()
    engine = GraphRAGEngine()
    cm = ConversationManager(mk, engine)
    
    # Start conversation
    call_sid = "test_call_123"
    conversation = cm.start_conversation(call_sid, "+1234567890")
    
    print(f"? Conversation Creation Test:")
    print(f"   Call SID: {call_sid}")
    print(f"   State: {conversation['state'].value}")
    
    # Test user input processing
    user_input = "I have a severe headache and feel nauseous"
    response = await cm.process_user_input(call_sid, user_input)
    
    print(f"? Input Processing Test:")
    print(f"   User Input: {user_input}")
    print(f"   Response: {response['message'][:100]}...")
    print(f"   Action: {response['action']}")
    print()
    
    await engine.shutdown()

async def test_phone_handler():
    """Test phone handler"""
    print("?? Testing Phone Handler...")
    
    mk = MedicalKnowledge()
    engine = GraphRAGEngine()
    cm = ConversationManager(mk, engine)
    ph = PhoneHandler(cm)
    
    # Test incoming call handling
    form_data = {
        "CallSid": "test_call_456",
        "From": "+1234567890"
    }
    
    response = await ph.handle_incoming_call(form_data)
    
    print(f"? Incoming Call Test:")
    print(f"   Call SID: {form_data['CallSid']}")
    print(f"   TwiML Generated: {len(str(response))} characters")
    print(f"   Response Type: {type(response).__name__}")
    print()
    
    await engine.shutdown()

async def test_emergency_scenario():
    """Test complete emergency scenario"""
    print("?? Testing Emergency Scenario...")
    
    mk = MedicalKnowledge()
    engine = GraphRAGEngine()
    cm = ConversationManager(mk, engine)
    
    # Emergency scenario
    call_sid = "emergency_test_789"
    conversation = cm.start_conversation(call_sid, "+1234567890")
    
    # User reports emergency symptoms
    emergency_input = "I'm having severe chest pain and I'm sweating a lot, the pain is going down my left arm"
    
    # Debug: Check symptom extraction
    extracted_symptoms = cm._extract_symptoms_from_text(emergency_input)
    print(f"   Extracted Symptoms: {extracted_symptoms}")
    
    # Debug: Check emergency detection directly
    emergency_check = mk.check_emergency_triggers(extracted_symptoms, emergency_input)
    print(f"   Direct Emergency Check: {emergency_check is not None}")
    if emergency_check:
        print(f"   Emergency Type: {emergency_check['emergency_type']}")
    
    response = await cm.process_user_input(call_sid, emergency_input)
    
    print(f"? Emergency Scenario Test:")
    print(f"   Input: {emergency_input}")
    print(f"   Detected as Emergency: {response.get('urgency') == 'emergency'}")
    print(f"   Action: {response['action']}")
    print(f"   Message: {response['message'][:100]}...")
    print()
    
    await engine.shutdown()

async def main():
    """Run all integration tests"""
    print("?? MedTriageAI Integration Tests")
    print("=" * 50)
    
    try:
        await test_medical_knowledge()
        await test_graph_rag_engine()
        await test_conversation_manager()
        await test_phone_handler()
        await test_emergency_scenario()
        
        print("?? All integration tests completed successfully!")
        
    except Exception as e:
        print(f"? Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())