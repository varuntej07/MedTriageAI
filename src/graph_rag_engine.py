import os
import json
import logging
from typing import Dict, List, Optional, Any
import networkx as nx
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import weaviate, but make it optional
try:
    import weaviate
    WEAVIATE_AVAILABLE = True
    logger.info("? Weaviate library available")
except ImportError:
    WEAVIATE_AVAILABLE = False
    logger.info("?? Weaviate library not available - using local knowledge graph only")

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available")

class GraphRAGEngine:
    """Microsoft GraphRAG-inspired engine for medical knowledge reasoning"""
    
    def __init__(self):
        self.medical_graph = None
        self.weaviate_client = None
        self.openai_client = None
        
        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info("? OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OpenAI API key not found or not available - using fallback analysis")
        
        # Initialize Weaviate vector database (optional)
        if WEAVIATE_AVAILABLE:
            self._initialize_weaviate()
            logger.info("Initializing Weaviate client...")
        
        # Initialize medical knowledge graph
        self._initialize_medical_graph()
        logger.info("Initializing medical knowledge graph...")
    
    def _initialize_weaviate(self):
        """Initialize Weaviate vector database connection"""
        try:
            weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
            self.weaviate_client = weaviate.Client(weaviate_url)
            
            # Test connection
            if self.weaviate_client.is_ready():
                logger.info("? Weaviate client connected")
            else:
                logger.warning("??  Weaviate not ready - using local knowledge graph only")
                self.weaviate_client = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate: {e}")
            self.weaviate_client = None
    
    def _initialize_medical_graph(self):
        """Initialize knowledge graph with medical entities and relationships"""
        self.medical_graph = nx.DiGraph()
        
        # Add core medical knowledge nodes and edges
        medical_knowledge = self._get_base_medical_knowledge()
        
        for condition, data in medical_knowledge.items():
            # Create a copy of data without conflicting keys
            node_data = data.copy()
            node_data["type"] = "condition"
            node_data["urgency_level"] = node_data.pop("urgency", "routine")  # Rename to avoid conflict
            
            # Add condition node
            self.medical_graph.add_node(condition, **node_data)
            
            # Add symptom nodes and relationships
            for symptom in data.get("primary_symptoms", []):
                self.medical_graph.add_node(symptom, type="symptom")
                self.medical_graph.add_edge(symptom, condition, relationship="indicates", weight=1.0)
            
            # Add risk factor relationships
            for risk_factor in data.get("risk_factors", []):
                self.medical_graph.add_node(risk_factor, type="risk_factor")
                self.medical_graph.add_edge(risk_factor, condition, relationship="increases_risk", weight=0.7)
        
        logger.info(f"? Medical graph initialized with {len(self.medical_graph.nodes)} nodes and {len(self.medical_graph.edges)} edges")
    
    def _get_base_medical_knowledge(self) -> Dict[str, Any]:
        """Base medical knowledge for the graph"""
        return {
            "acute_myocardial_infarction": {
                "primary_symptoms": ["chest pain", "sweating", "nausea", "radiating pain to arm"],
                "risk_factors": ["age over 65", "male gender", "smoking", "high blood pressure"],
                "urgency": "emergency",
                "follow_up_questions": [
                    "Is the pain radiating to your arm, neck, or jaw?",
                    "Are you sweating or feeling nauseous?",
                    "Do you have a history of heart disease?"
                ],
                "confidence_thresholds": {"high": 0.8, "medium": 0.6}
            },
            "stroke": {
                "primary_symptoms": ["sudden severe headache", "confusion", "weakness", "speech problems"],
                "risk_factors": ["age over 65", "high blood pressure", "diabetes", "smoking"],
                "urgency": "emergency",
                "follow_up_questions": [
                    "Is your face drooping on one side?",
                    "Can you raise both arms equally?",
                    "Is your speech slurred or garbled?"
                ],
                "confidence_thresholds": {"high": 0.85, "medium": 0.65}
            },
            "pneumonia": {
                "primary_symptoms": ["cough", "fever", "shortness of breath", "chest pain"],
                "risk_factors": ["age over 65", "chronic illness", "smoking", "weakened immune system"],
                "urgency": "urgent",
                "follow_up_questions": [
                    "How long have you had the fever?",
                    "Are you producing colored sputum when you cough?",
                    "Do you have chills or night sweats?"
                ],
                "confidence_thresholds": {"high": 0.75, "medium": 0.55}
            },
            "migraine": {
                "primary_symptoms": ["headache", "nausea", "light sensitivity", "sound sensitivity"],
                "risk_factors": ["female gender", "stress", "certain foods", "hormonal changes"],
                "urgency": "routine",
                "follow_up_questions": [
                    "Is this similar to headaches you've had before?",
                    "Do bright lights make it worse?",
                    "Are you experiencing any vision changes?"
                ],
                "confidence_thresholds": {"high": 0.7, "medium": 0.5}
            },
            "gastroenteritis": {
                "primary_symptoms": ["nausea", "vomiting", "diarrhea", "stomach pain"],
                "risk_factors": ["recent travel", "food poisoning", "viral infection"],
                "urgency": "routine",
                "follow_up_questions": [
                    "When did the symptoms start?",
                    "Have you eaten anything unusual recently?",
                    "Are you able to keep fluids down?"
                ],
                "confidence_thresholds": {"high": 0.65, "medium": 0.45}
            },
            "urinary_tract_infection": {
                "primary_symptoms": ["burning during urination", "frequent urination", "cloudy urine"],
                "risk_factors": ["female gender", "sexual activity", "diabetes", "catheter use"],
                "urgency": "urgent",
                "follow_up_questions": [
                    "Do you have pain in your lower back or side?",
                    "Is there blood in your urine?",
                    "Do you have fever or chills?"
                ],
                "confidence_thresholds": {"high": 0.7, "medium": 0.5}
            }
        }
    
    async def analyze_symptoms(self, symptoms: List[str], patient_info: Dict = None, follow_up_answers: Dict = None) -> Dict[str, Any]:
        """Analyze symptoms using GraphRAG approach"""
        try:
            # First, try AI-powered analysis if available
            if self.openai_client:
                ai_analysis = await self._openai_analysis(symptoms, patient_info, follow_up_answers)
                if ai_analysis:
                    return ai_analysis
            
            # Fallback to graph-based analysis
            return self._graph_based_analysis(symptoms, patient_info, follow_up_answers)
            
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            return self._emergency_fallback_analysis(symptoms)
    
    async def _openai_analysis(self, symptoms: List[str], patient_info: Dict = None, follow_up_answers: Dict = None) -> Optional[Dict[str, Any]]:
        """Use OpenAI for medical triage analysis"""
        if not self.openai_client or not OPENAI_AVAILABLE:
            return None
            
        try:
            # Construct prompt with medical knowledge context
            context = self._build_medical_context(symptoms)
            
            prompt = f"""
            You are a medical triage AI assistant. Based on the following symptoms and information, provide a triage assessment.
            
            IMPORTANT: You are NOT diagnosing - only helping with triage decisions. Always recommend professional medical evaluation.
            
            Symptoms: {', '.join(symptoms)}
            Patient Info: {patient_info or 'Not provided'}
            Follow-up Answers: {follow_up_answers or 'Not provided'}
            
            Medical Context:
            {context}
            
            Provide your assessment in the following JSON format:
            {{
                "urgency": "emergency|urgent|routine",
                "recommendation": "Clear next steps for the patient",
                "reasoning": ["reason1", "reason2", "reason3"],
                "confidence": 0.0-1.0,
                "differential_considerations": ["condition1", "condition2"],
                "red_flags": ["flag1", "flag2"] or null
            }}
            
            Guidelines:
            - "emergency": Immediate medical attention needed (911/ER)
            - "urgent": Same-day medical care needed  
            - "routine": Can wait for regular appointment
            - Always err on the side of caution
            - Include disclaimers about professional medical evaluation
            """
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical triage assistant. Provide structured, safe medical triage guidance."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse response
            content = response.choices[0].message.content
            analysis = json.loads(content)
            
            # Add metadata
            analysis["analysis_method"] = "openai_gpt4"
            analysis["timestamp"] = datetime.now().isoformat()
            
            return analysis
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return None
    
    def _graph_based_analysis(self, symptoms: List[str], patient_info: Dict = None, follow_up_answers: Dict = None) -> Dict[str, Any]:
        """Fallback graph-based analysis using NetworkX"""
        try:
            condition_scores = {}
            
            # Calculate scores for each condition based on symptom matches
            for condition in self.medical_graph.nodes():
                if self.medical_graph.nodes[condition].get("type") == "condition":
                    score = self._calculate_condition_score(condition, symptoms)
                    if score > 0:
                        condition_scores[condition] = score
            
            if not condition_scores:
                return self._emergency_fallback_analysis(symptoms)
            
            # Get top matching condition
            top_condition = max(condition_scores, key=condition_scores.get)
            top_score = condition_scores[top_condition]
            
            # Get condition data
            condition_data = self.medical_graph.nodes[top_condition]
            
            # Determine urgency and recommendation
            urgency = condition_data.get("urgency", "routine")
            confidence = min(top_score, 1.0)
            
            # Generate recommendation based on urgency
            recommendations = {
                "emergency": "Seek immediate emergency medical attention. Call 911 or go to the nearest emergency room.",
                "urgent": "Contact your healthcare provider today or visit an urgent care center.",
                "routine": "Schedule an appointment with your healthcare provider within the next few days."
            }
            
            recommendation = recommendations.get(urgency, recommendations["routine"])
            
            # Generate reasoning
            matched_symptoms = [s for s in symptoms if s in condition_data.get("primary_symptoms", [])]
            reasoning = [
                f"Your symptoms ({', '.join(matched_symptoms)}) are consistent with {top_condition.replace('_', ' ')}",
                f"This condition typically requires {urgency} medical attention",
                f"Match confidence: {confidence:.1%}"
            ]
            
            return {
                "urgency": urgency,
                "recommendation": recommendation,
                "reasoning": reasoning,
                "confidence": confidence,
                "differential_considerations": [top_condition.replace('_', ' ')],
                "red_flags": None,
                "analysis_method": "graph_based",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Graph analysis failed: {e}")
            return self._emergency_fallback_analysis(symptoms)
    
    def _calculate_condition_score(self, condition: str, symptoms: List[str]) -> float:
        """Calculate match score between symptoms and condition"""
        condition_data = self.medical_graph.nodes[condition]
        primary_symptoms = condition_data.get("primary_symptoms", [])
        
        if not primary_symptoms:
            return 0.0
        
        matches = sum(1 for symptom in symptoms if symptom.lower() in [ps.lower() for ps in primary_symptoms])
        return matches / len(primary_symptoms)
    
    def _build_medical_context(self, symptoms: List[str]) -> str:
        """Build medical context for AI analysis"""
        relevant_conditions = []
        
        for condition in self.medical_graph.nodes():
            if self.medical_graph.nodes[condition].get("type") == "condition":
                condition_data = self.medical_graph.nodes[condition]
                primary_symptoms = condition_data.get("primary_symptoms", [])
                
                # Check if any symptoms match
                if any(symptom.lower() in [ps.lower() for ps in primary_symptoms] for symptom in symptoms):
                    relevant_conditions.append({
                        "condition": condition.replace('_', ' '),
                        "symptoms": primary_symptoms,
                        "urgency": condition_data.get("urgency", "routine")
                    })
        
        context = "Relevant medical conditions to consider:\n"
        for condition in relevant_conditions[:5]:  # Limit to top 5
            context += f"- {condition['condition']} (urgency: {condition['urgency']})\n"
        
        return context
    
    def _emergency_fallback_analysis(self, symptoms: List[str]) -> Dict[str, Any]:
        """Emergency fallback when all other analysis methods fail"""
        # Simple keyword-based emergency detection
        emergency_keywords = ["chest pain", "severe headache", "difficulty breathing", "unconscious", "bleeding"]
        
        has_emergency_symptoms = any(
            keyword.lower() in ' '.join(symptoms).lower() 
            for keyword in emergency_keywords
        )
        
        if has_emergency_symptoms:
            urgency = "emergency"
            recommendation = "Seek immediate emergency medical attention. Call 911 or go to the nearest emergency room."
        else:
            urgency = "routine"
            recommendation = "Contact your healthcare provider to discuss your symptoms."
        
        return {
            "urgency": urgency,
            "recommendation": recommendation,
            "reasoning": ["Automated fallback analysis based on symptom keywords"],
            "confidence": 0.3,
            "differential_considerations": ["Multiple conditions possible"],
            "red_flags": ["System analysis limited - recommend professional evaluation"],
            "analysis_method": "fallback",
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_follow_up_questions(self, symptoms: List[str]) -> List[str]:
        """Generate targeted follow-up questions based on symptoms"""
        try:
            # Find relevant conditions
            relevant_conditions = []
            for condition in self.medical_graph.nodes():
                if self.medical_graph.nodes[condition].get("type") == "condition":
                    condition_data = self.medical_graph.nodes[condition]
                    primary_symptoms = condition_data.get("primary_symptoms", [])
                    
                    if any(symptom.lower() in [ps.lower() for ps in primary_symptoms] for symptom in symptoms):
                        relevant_conditions.append(condition_data)
            
            # Collect follow-up questions
            questions = []
            for condition_data in relevant_conditions[:2]:  # Top 2 conditions
                condition_questions = condition_data.get("follow_up_questions", [])
                questions.extend(condition_questions[:1])  # One question per condition
            
            # Add general questions if not enough specific ones
            if len(questions) < 2:
                general_questions = [
                    "How long have you been experiencing these symptoms?",
                    "On a scale of 1 to 10, how severe is your discomfort?",
                    "Have you taken any medications for these symptoms?",
                    "Do you have any chronic medical conditions?"
                ]
                questions.extend(general_questions)
            
            return questions[:3]  # Return max 3 questions
            
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            return [
                "How long have you been experiencing these symptoms?",
                "How severe would you rate your symptoms from 1 to 10?"
            ]
    
    async def shutdown(self):
        """Cleanup resources"""
        try:
            if self.weaviate_client:
                # Close Weaviate connection if needed
                pass
            logger.info("? GraphRAG Engine shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")