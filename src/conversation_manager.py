from typing import Dict, List, Optional, Any
from enum import Enum
import json
from datetime import datetime
import uuid

class ConversationState(Enum):
    GREETING = "greeting"
    COLLECTING_SYMPTOMS = "collecting_symptoms"
    FOLLOW_UP_QUESTIONS = "follow_up_questions"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    EMERGENCY = "emergency"
    COMPLETED = "completed"

class ConversationManager:
    """Manages conversation flow and state for medical triage calls"""
    
    def __init__(self, medical_knowledge, graph_rag_engine):
        self.medical_knowledge = medical_knowledge
        self.graph_rag_engine = graph_rag_engine
        self.conversations = {}  # In-memory storage for demo
    
    def start_conversation(self, call_sid: str, caller_number: str = None) -> Dict:
        """Initialize a new conversation"""
        conversation_id = str(uuid.uuid4())
        
        conversation = {
            "id": conversation_id,
            "call_sid": call_sid,
            "caller_number": caller_number,
            "state": ConversationState.GREETING,
            "created_at": datetime.now(),
            "symptoms": [],
            "patient_info": {},
            "follow_up_answers": {},
            "analysis_result": None,
            "interaction_count": 0,
            "emergency_detected": False
        }
        
        self.conversations[call_sid] = conversation
        return conversation
    
    def get_conversation(self, call_sid: str) -> Optional[Dict]:
        """Retrieve existing conversation"""
        return self.conversations.get(call_sid)
    
    async def process_user_input(self, call_sid: str, user_input: str) -> Dict:
        """Process user input and determine next response"""
        conversation = self.get_conversation(call_sid)
        if not conversation:
            return self._error_response("Conversation not found")
        
        conversation["interaction_count"] += 1
        current_state = conversation["state"]
        
        # Process input based on current state
        if current_state == ConversationState.GREETING:
            return await self._handle_greeting(conversation, user_input)
        elif current_state == ConversationState.COLLECTING_SYMPTOMS:
            return await self._handle_symptom_collection(conversation, user_input)
        elif current_state == ConversationState.FOLLOW_UP_QUESTIONS:
            return await self._handle_follow_up(conversation, user_input)
        elif current_state == ConversationState.ANALYSIS:
            return await self._handle_analysis_request(conversation, user_input)
        else:
            return self._get_default_response(conversation)
    
    async def _handle_greeting(self, conversation: Dict, user_input: str) -> Dict:
        """Handle initial greeting and move to symptom collection"""
        conversation["state"] = ConversationState.COLLECTING_SYMPTOMS
        
        # Extract any symptoms mentioned in greeting
        potential_symptoms = self._extract_symptoms_from_text(user_input)
        if potential_symptoms:
            conversation["symptoms"].extend(potential_symptoms)
            
            # Quick emergency check
            emergency = self.medical_knowledge.check_emergency_triggers(conversation["symptoms"], user_input)
            if emergency:
                conversation["state"] = ConversationState.EMERGENCY
                return self._create_emergency_response(emergency)
        
        return {
            "message": "I understand you're not feeling well. Can you describe your main symptoms? What's bothering you the most right now?",
            "action": "gather_input",
            "state": conversation["state"].value,
            "conversation_id": conversation["id"]
        }
    
    async def _handle_symptom_collection(self, conversation: Dict, user_input: str) -> Dict:
        """Collect and process initial symptoms"""
        # Extract symptoms from user input
        new_symptoms = self._extract_symptoms_from_text(user_input)
        conversation["symptoms"].extend(new_symptoms)
        
        # Remove duplicates
        conversation["symptoms"] = list(set(conversation["symptoms"]))
        
        # Check for emergencies
        emergency = self.medical_knowledge.check_emergency_triggers(conversation["symptoms"], user_input)
        if emergency:
            conversation["state"] = ConversationState.EMERGENCY
            conversation["emergency_detected"] = True
            return self._create_emergency_response(emergency)
        
        # If we have enough symptoms, move to follow-up questions
        if len(conversation["symptoms"]) >= 1:
            conversation["state"] = ConversationState.FOLLOW_UP_QUESTIONS
            return await self._generate_follow_up_questions(conversation)
        else:
            return {
                "message": "I need a bit more information. Can you tell me more about what you're experiencing? Any pain, fever, or other symptoms?",
                "action": "gather_input",
                "state": conversation["state"].value,
                "conversation_id": conversation["id"]
            }
    
    async def _handle_follow_up(self, conversation: Dict, user_input: str) -> Dict:
        """Handle follow-up question responses"""
        # Store the answer
        follow_up_key = f"follow_up_{len(conversation['follow_up_answers'])}"
        conversation["follow_up_answers"][follow_up_key] = user_input
        
        # Extract any additional symptoms
        additional_symptoms = self._extract_symptoms_from_text(user_input)
        if additional_symptoms:
            conversation["symptoms"].extend(additional_symptoms)
            conversation["symptoms"] = list(set(conversation["symptoms"]))
            
            # Re-check for emergencies
            emergency = self.medical_knowledge.check_emergency_triggers(conversation["symptoms"], user_input)
            if emergency:
                conversation["state"] = ConversationState.EMERGENCY
                return self._create_emergency_response(emergency)
        
        # If we have enough information, proceed to analysis
        if len(conversation["follow_up_answers"]) >= 2 or conversation["interaction_count"] >= 4:
            conversation["state"] = ConversationState.ANALYSIS
            return await self._perform_analysis(conversation)
        else:
            # Ask another follow-up question
            return await self._generate_follow_up_questions(conversation)
    
    async def _handle_analysis_request(self, conversation: Dict, user_input: str) -> Dict:
        """Handle requests during analysis phase"""
        if not conversation["analysis_result"]:
            return await self._perform_analysis(conversation)
        
        conversation["state"] = ConversationState.COMPLETED
        return {
            "message": "Thank you for using our medical triage service. Please take care and follow the recommendations provided. If your condition worsens, don't hesitate to seek immediate medical attention.",
            "action": "end_call",
            "state": conversation["state"].value,
            "conversation_id": conversation["id"]
        }
    
    async def _generate_follow_up_questions(self, conversation: Dict) -> Dict:
        """Generate targeted follow-up questions based on symptoms"""
        try:
            # Get AI-generated follow-up questions
            questions = await self.graph_rag_engine.generate_follow_up_questions(
                conversation["symptoms"]
            )
            
            if questions:
                question = questions[0]  # Use the first question
                return {
                    "message": question,
                    "action": "gather_input",
                    "state": conversation["state"].value,
                    "conversation_id": conversation["id"]
                }
            else:
                # Fallback questions
                return self._get_fallback_question(conversation)
                
        except Exception as e:
            print(f"Error generating follow-up questions: {e}")
            return self._get_fallback_question(conversation)
    
    def _get_fallback_question(self, conversation: Dict) -> Dict:
        """Get fallback questions when AI is unavailable"""
        fallback_questions = [
            "How long have you been experiencing these symptoms?",
            "On a scale of 1 to 10, how would you rate your pain or discomfort?",
            "Have you had these symptoms before?",
            "Are you taking any medications currently?"
        ]
        
        question_index = len(conversation["follow_up_answers"]) % len(fallback_questions)
        return {
            "message": fallback_questions[question_index],
            "action": "gather_input",
            "state": conversation["state"].value,
            "conversation_id": conversation["id"]
        }
    
    async def _perform_analysis(self, conversation: Dict) -> Dict:
        """Perform medical analysis using GraphRAG"""
        try:
            # Prepare patient information
            patient_info = conversation.get("patient_info", {})
            
            # Get analysis from GraphRAG engine
            analysis = await self.graph_rag_engine.analyze_symptoms(
                conversation["symptoms"],
                patient_info,
                conversation["follow_up_answers"]
            )
            
            conversation["analysis_result"] = analysis
            conversation["state"] = ConversationState.RECOMMENDATION
            
            return self._create_recommendation_response(analysis, conversation)
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return self._get_fallback_analysis(conversation)
    
    def _create_recommendation_response(self, analysis: Dict, conversation: Dict) -> Dict:
        """Create recommendation response based on analysis"""
        urgency = analysis.get("urgency", "routine")
        recommendation = analysis.get("recommendation", "Consult healthcare provider")
        reasoning = analysis.get("reasoning", [])
        confidence = analysis.get("confidence", 0.5)
        
        # Create response message
        if urgency == "emergency":
            message = f"?? URGENT: {recommendation}. "
        elif urgency == "urgent":
            message = f"This appears to require prompt attention. {recommendation}. "
        else:
            message = f"Based on your symptoms, {recommendation}. "
        
        # Add reasoning
        if reasoning:
            message += f"\n\nHere's why: {' '.join(reasoning[:2])}"
        
        # Add confidence note if low
        if confidence < 0.6:
            message += "\n\nPlease note: I recommend seeking professional medical advice for a thorough evaluation."
        
        # Add disclaimer
        message += "\n\n?? IMPORTANT: This is not a medical diagnosis. This triage assessment is meant to help guide your next steps. Please consult with healthcare professionals for proper medical care."
        
        return {
            "message": message,
            "action": "provide_recommendation" if urgency != "emergency" else "emergency_action",
            "state": conversation["state"].value,
            "conversation_id": conversation["id"],
            "urgency": urgency,
            "confidence": confidence
        }
    
    def _create_emergency_response(self, emergency: Dict) -> Dict:
        """Create emergency response"""
        return {
            "message": f"?? MEDICAL EMERGENCY DETECTED ??\n\n{emergency['action']}\n\nThis appears to be a serious medical emergency. Please seek immediate medical attention. If you are experiencing a life-threatening emergency, hang up and call 911 now.",
            "action": "emergency_action",
            "state": ConversationState.EMERGENCY.value,
            "urgency": "emergency",
            "confidence": emergency.get("confidence", 0.9)
        }
    
    def _get_fallback_analysis(self, conversation: Dict) -> Dict:
        """Fallback analysis when AI is unavailable"""
        symptoms_count = len(conversation["symptoms"])
        
        if symptoms_count >= 3:
            urgency = "urgent"
            message = "Based on the number of symptoms you've described, I recommend contacting your healthcare provider or visiting an urgent care center today."
        elif symptoms_count >= 2:
            urgency = "routine"
            message = "Your symptoms warrant medical attention. Please consider scheduling an appointment with your healthcare provider within the next few days."
        else:
            urgency = "routine"
            message = "While your symptoms may not be serious, it's always best to consult with a healthcare professional if you're concerned."
        
        message += "\n\n?? IMPORTANT: This is not a medical diagnosis. Please consult with healthcare professionals for proper medical care."
        
        return {
            "message": message,
            "action": "provide_recommendation",
            "state": ConversationState.RECOMMENDATION.value,
            "conversation_id": conversation["id"],
            "urgency": urgency,
            "confidence": 0.5
        }
    
    def _extract_symptoms_from_text(self, text: str) -> List[str]:
        """Extract symptoms from user text input"""
        text_lower = text.lower()
        symptoms = []
        
        # Common symptom keywords
        symptom_keywords = {
            "chest pain": ["chest pain", "heart pain", "crushing chest pain", "chest pressure", "chest tightness"],
            "pain": ["pain", "hurt", "ache", "sore"],
            "fever": ["fever", "hot", "temperature", "chills"],
            "headache": ["headache", "head pain", "migraine"],
            "nausea": ["nausea", "sick to stomach", "queasy"],
            "vomiting": ["vomiting", "throwing up", "vomit"],
            "diarrhea": ["diarrhea", "loose stools", "bowel"],
            "cough": ["cough", "coughing"],
            "shortness of breath": ["breathe", "breathing", "breath", "air", "shortness of breath"],
            "dizziness": ["dizzy", "lightheaded", "faint"],
            "fatigue": ["tired", "exhausted", "fatigue", "weak"],
            "back pain": ["back"],
            "stomach pain": ["stomach", "belly", "abdomen"],
            "sore throat": ["throat", "swallow"],
            "sweating": ["sweat", "sweating", "perspiring"],
            "radiating pain": ["radiating pain", "pain going down", "pain in my arm", "pain to arm", "pain down my arm"]
        }
        
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                symptoms.append(symptom)
        
        return symptoms
    
    def _get_default_response(self, conversation: Dict) -> Dict:
        """Get default response when state is unclear"""
        return {
            "message": "I'm here to help assess your symptoms. Can you tell me what's bothering you today?",
            "action": "gather_input",
            "state": ConversationState.COLLECTING_SYMPTOMS.value,
            "conversation_id": conversation["id"]
        }
    
    def _error_response(self, error_message: str) -> Dict:
        """Return error response"""
        return {
            "message": "I'm sorry, there was an issue with our system. Please try calling back or seek medical attention if this is urgent.",
            "action": "end_call",
            "error": error_message
        }
    
    def get_conversation_summary(self, call_sid: str) -> Optional[Dict]:
        """Get summary of conversation for logging/analysis"""
        conversation = self.get_conversation(call_sid)
        if not conversation:
            return None
        
        return {
            "conversation_id": conversation["id"],
            "duration": (datetime.now() - conversation["created_at"]).total_seconds(),
            "symptoms_collected": conversation["symptoms"],
            "final_state": conversation["state"].value,
            "emergency_detected": conversation["emergency_detected"],
            "analysis_performed": conversation["analysis_result"] is not None,
            "interaction_count": conversation["interaction_count"]
        }