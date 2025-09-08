from typing import Dict, List, Optional, Any, Set
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class UrgencyLevel(Enum):
    EMERGENCY = "emergency"
    URGENT = "urgent" 
    ROUTINE = "routine"

class MedicalKnowledge:
    """Medical knowledge base for emergency detection and triage logic"""
    
    def __init__(self):
        self.conditions = self._initialize_medical_conditions()
        self.emergency_triggers = self._initialize_emergency_triggers()
        self.symptom_mappings = self._initialize_symptom_mappings()
        logger.info(f"✅ Medical Knowledge initialized with {len(self.conditions)} conditions")
    
    def _initialize_medical_conditions(self) -> Dict[str, Any]:
        """Initialize comprehensive medical condition database"""
        return {
            # EMERGENCY CONDITIONS
            "acute_myocardial_infarction": {
                "name": "Acute Myocardial Infarction (Heart Attack)",
                "primary_symptoms": ["chest pain", "sweating", "nausea", "vomiting", "radiating pain"],
                "secondary_symptoms": ["shortness of breath", "dizziness", "fatigue", "cold sweat"],
                "risk_factors": ["age over 45 male", "age over 55 female", "smoking", "high blood pressure", "diabetes", "high cholesterol"],
                "urgency": UrgencyLevel.EMERGENCY,
                "emergency_score": 10,
                "follow_up_questions": [
                    "Is the chest pain crushing or squeezing?",
                    "Does the pain radiate to your arm, neck, or jaw?",
                    "Are you sweating profusely?",
                    "Do you feel nauseous or have you vomited?",
                    "Do you have a history of heart disease?"
                ],
                "confidence_thresholds": {"high": 0.8, "medium": 0.6, "low": 0.4}
            },
            
            "stroke": {
                "name": "Stroke / Cerebrovascular Accident",
                "primary_symptoms": ["sudden severe headache", "confusion", "weakness", "speech problems", "vision problems"],
                "secondary_symptoms": ["dizziness", "loss of balance", "facial drooping"],
                "risk_factors": ["age over 65", "high blood pressure", "diabetes", "smoking", "atrial fibrillation"],
                "urgency": UrgencyLevel.EMERGENCY,
                "emergency_score": 10,
                "follow_up_questions": [
                    "Is your face drooping on one side?",
                    "Can you raise both arms and keep them up?",
                    "Is your speech slurred or strange?",
                    "When did these symptoms start?",
                    "Do you have high blood pressure?"
                ],
                "confidence_thresholds": {"high": 0.85, "medium": 0.65, "low": 0.45}
            },
            
            "anaphylaxis": {
                "name": "Severe Allergic Reaction (Anaphylaxis)",
                "primary_symptoms": ["difficulty breathing", "swelling", "rash", "hives"],
                "secondary_symptoms": ["rapid pulse", "dizziness", "nausea", "vomiting"],
                "risk_factors": ["known allergies", "recent exposure to allergen", "previous anaphylaxis"],
                "urgency": UrgencyLevel.EMERGENCY,
                "emergency_score": 10,
                "follow_up_questions": [
                    "Are you having trouble breathing or swallowing?",
                    "Is your face, lips, or tongue swelling?",
                    "Did you recently eat something or take medication you're allergic to?",
                    "Do you have an EpiPen with you?",
                    "Have you had severe allergic reactions before?"
                ],
                "confidence_thresholds": {"high": 0.9, "medium": 0.7, "low": 0.5}
            },
            
            # URGENT CONDITIONS  
            "pneumonia": {
                "name": "Pneumonia",
                "primary_symptoms": ["cough", "fever", "shortness of breath", "chest pain"],
                "secondary_symptoms": ["fatigue", "chills", "sweating", "rapid breathing"],
                "risk_factors": ["age over 65", "chronic illness", "smoking", "weakened immune system"],
                "urgency": UrgencyLevel.URGENT,
                "emergency_score": 6,
                "follow_up_questions": [
                    "How high is your fever?",
                    "Are you coughing up colored or bloody sputum?",
                    "How long have you had these symptoms?",
                    "Do you have any chronic health conditions?",
                    "Are you having trouble breathing even at rest?"
                ],
                "confidence_thresholds": {"high": 0.75, "medium": 0.55, "low": 0.35}
            },
            
            "urinary_tract_infection": {
                "name": "Urinary Tract Infection",
                "primary_symptoms": ["burning during urination", "frequent urination", "urgency", "cloudy urine"],
                "secondary_symptoms": ["pelvic pain", "strong-smelling urine", "blood in urine"],
                "risk_factors": ["female gender", "sexual activity", "diabetes", "pregnancy"],
                "urgency": UrgencyLevel.URGENT,
                "emergency_score": 4,
                "follow_up_questions": [
                    "Do you have pain in your back or side?",
                    "Is there blood in your urine?",
                    "Do you have fever or chills?",
                    "How long have you had these symptoms?",
                    "Are you pregnant?"
                ],
                "confidence_thresholds": {"high": 0.7, "medium": 0.5, "low": 0.3}
            },
            
            # ROUTINE CONDITIONS
            "migraine": {
                "name": "Migraine Headache",
                "primary_symptoms": ["severe headache", "nausea", "light sensitivity", "sound sensitivity"],
                "secondary_symptoms": ["vision changes", "aura", "vomiting"],
                "risk_factors": ["female gender", "stress", "hormonal changes", "certain foods"],
                "urgency": UrgencyLevel.ROUTINE,
                "emergency_score": 2,
                "follow_up_questions": [
                    "Is this headache similar to ones you've had before?",
                    "Do you see flashing lights or have vision changes?",
                    "Does light or sound make it worse?",
                    "Have you identified any triggers?",
                    "Are you taking any headache medications?"
                ],
                "confidence_thresholds": {"high": 0.7, "medium": 0.5, "low": 0.3}
            },
            
            "common_cold": {
                "name": "Common Cold / Upper Respiratory Infection",
                "primary_symptoms": ["runny nose", "congestion", "cough", "sneezing"],
                "secondary_symptoms": ["sore throat", "mild headache", "fatigue"],
                "risk_factors": ["recent cold exposure", "weakened immune system", "stress"],
                "urgency": UrgencyLevel.ROUTINE,
                "emergency_score": 1,
                "follow_up_questions": [
                    "How long have you had these symptoms?",
                    "Do you have a fever?",
                    "Are you able to breathe through your nose?",
                    "Have you been around anyone who was sick?",
                    "Are your symptoms getting worse?"
                ],
                "confidence_thresholds": {"high": 0.6, "medium": 0.4, "low": 0.2}
            },
            
            "gastroenteritis": {
                "name": "Gastroenteritis / Stomach Bug",
                "primary_symptoms": ["nausea", "vomiting", "diarrhea", "stomach pain"],
                "secondary_symptoms": ["fever", "cramps", "dehydration"],
                "risk_factors": ["recent travel", "food poisoning", "viral exposure"],
                "urgency": UrgencyLevel.ROUTINE,
                "emergency_score": 3,
                "follow_up_questions": [
                    "When did your symptoms start?",
                    "Are you able to keep fluids down?",
                    "Have you eaten anything unusual recently?",
                    "Do you have a fever?",
                    "Are you showing signs of dehydration?"
                ],
                "confidence_thresholds": {"high": 0.65, "medium": 0.45, "low": 0.25}
            }
        }
    
    def _initialize_emergency_triggers(self) -> List[Dict[str, Any]]:
        """Define emergency trigger patterns"""
        return [
            {
                "name": "chest_pain_emergency",
                "required_symptoms": ["chest pain"],
                "additional_indicators": ["sweating", "sweat", "nausea", "radiating", "arm", "shortness of breath"],
                "min_indicators": 1,
                "action": "Call 911 immediately. This could be a heart attack.",
                "confidence": 0.9
            },
            {
                "name": "stroke_emergency", 
                "required_symptoms": ["confusion", "weakness", "speech problems"],
                "additional_indicators": ["sudden severe headache", "facial drooping", "vision problems"],
                "min_indicators": 1,
                "action": "Call 911 immediately. This could be a stroke. Note the time symptoms started.",
                "confidence": 0.9
            },
            {
                "name": "severe_allergic_reaction",
                "required_symptoms": ["difficulty breathing"],
                "additional_indicators": ["swelling", "hives", "rash", "rapid pulse"],
                "min_indicators": 1,
                "action": "Call 911 immediately. Use EpiPen if available. This appears to be a severe allergic reaction.",
                "confidence": 0.95
            },
            {
                "name": "severe_breathing_difficulty",
                "required_symptoms": ["severe shortness of breath", "difficulty breathing"],
                "additional_indicators": ["chest pain", "blue lips", "cannot speak in full sentences"],
                "min_indicators": 0,
                "action": "Call 911 immediately. Seek emergency medical attention for severe breathing difficulty.",
                "confidence": 0.85
            },
            {
                "name": "loss_of_consciousness",
                "required_symptoms": ["unconscious", "fainted", "passed out"],
                "additional_indicators": ["seizure", "unresponsive"],
                "min_indicators": 0,
                "action": "Call 911 immediately. Do not leave the person alone.",
                "confidence": 0.95
            },
            {
                "name": "severe_bleeding",
                "required_symptoms": ["severe bleeding", "heavy bleeding", "bleeding won't stop"],
                "additional_indicators": ["dizziness", "weakness", "pale"],
                "min_indicators": 0,
                "action": "Call 911 immediately. Apply direct pressure to bleeding wounds.",
                "confidence": 0.9
            },
            {
                "name": "mental_health_crisis",
                "required_symptoms": ["suicidal thoughts", "want to hurt myself", "thoughts of suicide"],
                "additional_indicators": ["depression", "hopeless", "want to die"],
                "min_indicators": 0,
                "action": "Call 988 (Suicide & Crisis Lifeline) or 911 immediately. You are not alone and help is available.",
                "confidence": 1.0
            }
        ]
    
    def _initialize_symptom_mappings(self) -> Dict[str, List[str]]:
        """Map symptom variations to standard terms"""
        return {
            "chest pain": ["chest pain", "chest pressure", "chest tightness", "heart pain", "crushing chest pain"],
            "shortness of breath": ["shortness of breath", "difficulty breathing", "can't breathe", "breathless", "winded"],
            "headache": ["headache", "head pain", "migraine", "head hurts"],
            "nausea": ["nausea", "feel sick", "queasy", "sick to stomach"],
            "vomiting": ["vomiting", "throwing up", "puking", "vomit"],
            "fever": ["fever", "high temperature", "hot", "chills", "sweating"],
            "dizziness": ["dizzy", "lightheaded", "faint", "unsteady"],
            "weakness": ["weak", "weakness", "can't move", "paralyzed", "limp"],
            "confusion": ["confused", "disoriented", "can't think", "foggy"],
            "speech problems": ["can't speak", "slurred speech", "speech unclear", "trouble talking"],
            "swelling": ["swelling", "swollen", "puffed up", "bloated face"],
            "rash": ["rash", "red skin", "hives", "itchy skin", "bumps"]
        }
    
    def check_emergency_triggers(self, symptoms: List[str], original_text: str = "") -> Optional[Dict[str, Any]]:
        """Check if symptoms match any emergency trigger patterns"""
        if not symptoms and not original_text:
            return None
        
        # Combine symptoms and original text for comprehensive checking
        search_text = ' '.join(symptoms).lower()
        if original_text:
            search_text += ' ' + original_text.lower()
        
        for trigger in self.emergency_triggers:
            if self._matches_emergency_pattern_text(search_text, trigger):
                return {
                    "emergency_type": trigger["name"],
                    "action": trigger["action"],
                    "confidence": trigger["confidence"],
                    "matched_symptoms": [s for s in symptoms if any(req.lower() in s.lower() for req in trigger["required_symptoms"])],
                    "urgency": "emergency"
                }
        
        return None
    
    def _matches_emergency_pattern(self, symptoms: List[str], trigger: Dict[str, Any]) -> bool:
        """Check if symptoms match an emergency trigger pattern"""
        symptoms_text = ' '.join(symptoms).lower()
        
        # Check required symptoms
        required_symptoms = trigger.get("required_symptoms", [])
        has_required = any(req.lower() in symptoms_text for req in required_symptoms)
        
        if not has_required and required_symptoms:
            return False
        
        # Check additional indicators
        additional_indicators = trigger.get("additional_indicators", [])
        min_indicators = trigger.get("min_indicators", 1)
        
        if additional_indicators:
            indicator_count = sum(
                1 for indicator in additional_indicators
                if indicator.lower() in symptoms_text
            )
            
            if indicator_count < min_indicators:
                return False
        
        return True
    
    def _matches_emergency_pattern_text(self, text: str, trigger: Dict[str, Any]) -> bool:
        """Check if text matches an emergency trigger pattern"""
        # Check required symptoms
        required_symptoms = trigger.get("required_symptoms", [])
        has_required = any(req.lower() in text for req in required_symptoms)
        
        if not has_required and required_symptoms:
            return False
        
        # Check additional indicators
        additional_indicators = trigger.get("additional_indicators", [])
        min_indicators = trigger.get("min_indicators", 1)
        
        if additional_indicators:
            indicator_count = sum(
                1 for indicator in additional_indicators
                if indicator.lower() in text
            )
            
            if indicator_count < min_indicators:
                return False
        
        return True
    
    def get_condition_by_symptoms(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """Get matching conditions based on symptoms"""
        if not symptoms:
            return []
        
        # Simple normalization - just convert to lowercase for comparison
        normalized_symptoms = [s.lower().strip() for s in symptoms]
        matches = []
        
        for condition_id, condition in self.conditions.items():
            score = self._calculate_symptom_match_score(normalized_symptoms, condition)
            
            if score > 0:
                matches.append({
                    "condition_id": condition_id,
                    "condition": condition,
                    "match_score": score,
                    "urgency": condition["urgency"].value,
                    "emergency_score": condition["emergency_score"]
                })
        
        # Sort by emergency score first, then match score
        matches.sort(key=lambda x: (x["emergency_score"], x["match_score"]), reverse=True)
        return matches
    
    def _calculate_symptom_match_score(self, symptoms: List[str], condition: Dict[str, Any]) -> float:
        """Calculate how well symptoms match a condition"""
        primary_symptoms = [s.lower() for s in condition.get("primary_symptoms", [])]
        secondary_symptoms = [s.lower() for s in condition.get("secondary_symptoms", [])]
        
        primary_matches = sum(
            1 for symptom in symptoms 
            if any(ps in symptom.lower() or symptom.lower() in ps for ps in primary_symptoms)
        )
        
        secondary_matches = sum(
            1 for symptom in symptoms
            if any(ss in symptom.lower() or symptom.lower() in ss for ss in secondary_symptoms)
        )
        
        # Weight primary symptoms more heavily
        total_primary = len(primary_symptoms)
        total_secondary = len(secondary_symptoms)
        
        if total_primary == 0:
            return 0.0
        
        primary_score = primary_matches / total_primary
        secondary_score = secondary_matches / total_secondary if total_secondary > 0 else 0
        
        # Combined score with primary symptoms weighted 70%, secondary 30%
        return (primary_score * 0.7) + (secondary_score * 0.3)
    
    def get_follow_up_questions(self, condition_id: str) -> List[str]:
        """Get follow-up questions for a specific condition"""
        condition = self.conditions.get(condition_id)
        if condition:
            return condition.get("follow_up_questions", [])
        return []
    
    def assess_urgency(self, symptoms: List[str], patient_info: Dict = None) -> Dict[str, Any]:
        """Assess urgency level based on symptoms and patient information"""
        # First check for emergencies
        emergency = self.check_emergency_triggers(symptoms)
        if emergency:
            return {
                "urgency": "emergency",
                "reasoning": [f"Emergency detected: {emergency['emergency_type']}"],
                "confidence": emergency["confidence"],
                "action_required": emergency["action"]
            }
        
        # Get condition matches
        matches = self.get_condition_by_symptoms(symptoms)
        
        if not matches:
            return {
                "urgency": "routine",
                "reasoning": ["No specific condition patterns identified"],
                "confidence": 0.3,
                "action_required": "Consider consulting healthcare provider if symptoms persist"
            }
        
        top_match = matches[0]
        
        return {
            "urgency": top_match["urgency"],
            "reasoning": [
                f"Symptoms match {top_match['condition']['name']}",
                f"Match confidence: {top_match['match_score']:.1%}"
            ],
            "confidence": top_match["match_score"],
            "action_required": self._get_urgency_action(top_match["urgency"])
        }
    
    def _get_urgency_action(self, urgency: str) -> str:
        """Get recommended action based on urgency level"""
        actions = {
            "emergency": "Seek immediate emergency medical attention (call 911)",
            "urgent": "Contact healthcare provider today or visit urgent care",
            "routine": "Schedule appointment with healthcare provider"
        }
        return actions.get(urgency, actions["routine"])
    
    def get_medical_disclaimer(self) -> str:
        """Get standard medical disclaimer"""
        return (
            "⚠️ IMPORTANT DISCLAIMER: This assessment is for informational purposes only "
            "and does not constitute medical advice, diagnosis, or treatment. Always consult "
            "with qualified healthcare professionals for proper medical evaluation and care. "
            "In case of emergency, call 911 immediately."
        )