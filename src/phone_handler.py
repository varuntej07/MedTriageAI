from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PhoneHandler:
    """Handles Twilio phone calls and speech processing for medical triage"""
    
    def __init__(self, conversation_manager):
        self.conversation_manager = conversation_manager
        self.twilio_client = None
        
        # Dynamic base URL
        self.base_url = os.getenv("VERCEL_URL", "https://med-triage-ai-git-master-varuntej07s-projects.vercel.app/")
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        
        logger.info(f"📞 Using base URL: {self.base_url}")
        
        # Initialize Twilio client if credentials are available
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if account_sid and auth_token:
            try:
                self.twilio_client = Client(account_sid, auth_token)
                logger.info("✅ Twilio client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
        else:
            logger.warning("⚠️ Twilio credentials not found - calls will use demo responses")
    
    async def handle_incoming_call(self, form_data: Dict[str, Any]) -> VoiceResponse:
        """Handle incoming phone call from Twilio"""
        try:
            # Extract call information
            call_sid = form_data.get("CallSid", "demo_call")
            caller_number = form_data.get("From", "unknown")
            
            logger.info(f"?? Incoming call: {call_sid} from {caller_number}")
            
            # Start new conversation
            conversation = self.conversation_manager.start_conversation(call_sid, caller_number)
            
            # Create TwiML response
            response = VoiceResponse()
            
            # Welcome message
            welcome_message = (
                "Hello, you've reached MedTriageAI, Please describe what's bothering you today."
            )
            
            response.say(welcome_message, voice="alice")
            
            # Gather user input
            gather = response.gather(
                input="speech",
                timeout=10,
                speech_timeout="auto",
                action=f"{self.base_url}voice/gather",
                method="POST"
            )
            gather.say("I'm listening. Please describe your symptoms", voice="alice")
            
            # Fallback if no input received
            response.say("I didn't hear anything. Please call back if you need medical assistance.")
            response.hangup()
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling incoming call: {e}")
            return self._create_error_response()
    
    async def handle_speech_input(self, form_data: Dict[str, Any]) -> VoiceResponse:
        """Process speech input from caller"""
        try:
            call_sid = form_data.get("CallSid", "demo_call")
            speech_result = form_data.get("SpeechResult", "")
            confidence = float(form_data.get("Confidence", 0.0))
            
            logger.info(f"?? Speech input for {call_sid}: '{speech_result}' (confidence: {confidence})")
            
            # Handle low confidence speech
            if confidence < 0.3:
                return self._handle_unclear_speech()
            
            # Process input through conversation manager
            conversation_response = await self.conversation_manager.process_user_input(call_sid, speech_result)
            
            # Convert to TwiML response
            return self._create_twiml_response(conversation_response)
            
        except Exception as e:
            logger.error(f"Error processing speech input: {e}")
            return self._create_error_response()
    
    def _create_twiml_response(self, conversation_response: Dict[str, Any]) -> VoiceResponse:
        """Convert conversation manager response to TwiML"""
        response = VoiceResponse()
        
        action = conversation_response.get("action", "gather_input")
        message = conversation_response.get("message", "I'm here to help with your symptoms.")
        urgency = conversation_response.get("urgency", "routine")
        
        # Handle different response types
        if action == "emergency_action":
            # Emergency - speak urgently and provide immediate guidance
            response.say(message, voice="alice")
            response.say("Please hang up and call 911 immediately if this is a life-threatening emergency.")
            response.hangup()
            
        elif action == "provide_recommendation":
            # Final recommendation
            response.say(message, voice="alice")
            
            # Ask if they need anything else
            gather = response.gather(
                input="speech",
                timeout=5,
                speech_timeout="auto",
                action=f"{self.base_url}voice/gather",
                method="POST"
            )
            gather.say("Is there anything else I can help you with today?")
            
            # End call if no response
            response.say("Thank you for using MedTriageAI. Take care and seek medical attention if your condition worsens.")
            response.hangup()
            
        elif action == "gather_input":
            # Continue conversation - gather more input
            response.say(message, voice="alice")
            
            gather = response.gather(
                input="speech",
                timeout=15,
                speech_timeout="auto",
                action=f"{self.base_url}voice/gather",
                method="POST"
            )
            
            # Timeout fallback
            response.say("I didn't hear a response. Let me ask again: Can you describe your symptoms?")
            
            gather2 = response.gather(
                input="speech",
                timeout=10,
                speech_timeout="auto",
                action=f"{self.base_url}voice/gather",
                method="POST"
            )
            
            response.say("I'm having trouble hearing you. Please call back when you can speak clearly.")
            response.hangup()
            
        elif action == "end_call":
            # End the call
            response.say(message, voice="alice")
            response.say("Thank you for calling. Please seek appropriate medical care. Goodbye.")
            response.hangup()
            
        else:
            # Default fallback
            response.say(message, voice="alice")
            response.hangup()
        
        return response
    
    def _handle_unclear_speech(self) -> VoiceResponse:
        """Handle cases where speech recognition confidence is low"""
        response = VoiceResponse()
        
        response.say("I had trouble understanding what you said. Please speak clearly and describe your main symptoms.")
        
        gather = response.gather(
            input="speech",
            timeout=10,
            speech_timeout="auto",
            action=f"{self.base_url}voice/gather",
            method="POST"
        )
        
        response.say("I'm still having trouble hearing you. Please call back when you can speak more clearly.")
        response.hangup()
        
        return response
    
    def _create_error_response(self) -> VoiceResponse:
        """Create error response for system failures"""
        response = VoiceResponse()
        
        response.say(
            "I'm sorry, there's a technical issue with our system right now. "
            "If this is a medical emergency, please hang up and call 911 immediately. "
            "Otherwise, please try calling back in a few minutes."
        )
        response.hangup()
        
        return response
    
    def get_call_log(self, call_sid: str) -> Dict[str, Any]:
        """Get call details from Twilio (if available)"""
        if not self.twilio_client:
            return {"error": "Twilio client not available"}
        
        try:
            call = self.twilio_client.calls(call_sid).fetch()
            return {
                "call_sid": call.sid,
                "from_number": call.from_,
                "to_number": call.to,
                "status": call.status,
                "duration": call.duration,
                "start_time": call.start_time,
                "end_time": call.end_time
            }
        except Exception as e:
            logger.error(f"Error fetching call log: {e}")
            return {"error": str(e)}