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
        
        raw = os.getenv("PUBLIC_BASE_URL") or os.getenv("VERCEL_URL") or ""
        if raw.startswith("http"):
            self.base_url = raw.rstrip("/")
        elif raw:
            self.base_url = f"https://{raw}".rstrip("/")
        else:
            self.base_url = "https://med-triage-ai-git-master-varuntej07s-projects.vercel.app"

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
            
            logger.info(f"📞 Incoming call: {call_sid} from {caller_number}")
            
            # Start new conversation
            conversation = self.conversation_manager.start_conversation(call_sid, caller_number)
            
            # Create TwiML response
            response = VoiceResponse()
            
            # Welcome message
            welcome_message = (
                "Hello, I'm your medical assistant. Describe what's bothering you today."
            )
            
            response.say(welcome_message, voice="alice")
            
            # Gather user input
            gather = response.gather(
                input="speech",
                timeout=15,
                speech_timeout="auto",
                action=f"{self.base_url}/voice/gather",
                method="POST",
                language="en-US",  # Explicit language setting
                profanity_filter="false"  # Disable profanity filter for medical terms
            )
            gather.say("I'm listening...", voice="alice")
            
            # Fallback if no input received
            response.say("I didn't hear you. can you repeat it clearly.")
            response.say("If this is an emergency, please hang up and call 9-1-1 immediately.")
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
            
            logger.info(f"🗣️ Speech input for {call_sid}: '{speech_result}' (confidence: {confidence})")
            
            # Handle low confidence speech - lowered threshold
            if confidence < 0.2:
                logger.warning(f"Low confidence speech: {confidence}")
                return self._handle_unclear_speech()
            
            # Log empty speech result
            if not speech_result.strip():
                logger.warning("Empty speech result received")
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
                timeout=8,
                speech_timeout="auto",
                action=f"{self.base_url}/voice/gather",
                method="POST",
                language="en-US"
            )
            gather.say("Is there anything else I can help you with today?", voice="alice")
            
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
                action=f"{self.base_url}/voice/gather",
                method="POST",
                language="en-US"
            )
            
            # Timeout fallback
            response.say("I didn't hear a response. Let me ask again: Can you describe your symptoms?", voice="alice")
            
            gather2 = response.gather(
                input="speech",
                timeout=12,
                speech_timeout="auto",
                action=f"{self.base_url}/voice/gather",
                method="POST",
                language="en-US"
            )
            
            response.say("I'm having trouble hearing you. Please call back when you can speak clearly.", voice="alice")
            response.hangup()
            
        elif action == "end_call":
            # End the call
            response.say(message, voice="alice")
            response.say("Thank you for calling. Please seek appropriate medical care. Goodbye.", voice="alice")
            response.hangup()
            
        else:
            # Default fallback
            response.say(message, voice="alice")
            response.hangup()
        
        return response
    
    def _handle_unclear_speech(self) -> VoiceResponse:
        """Handle cases where speech recognition confidence is low"""
        response = VoiceResponse()
        
        response.say("I had trouble understanding what you said. Please speak clearly and describe your main symptoms.", voice="alice")
        
        gather = response.gather(
            input="speech",
            timeout=12,
            speech_timeout="auto",
            action=f"{self.base_url}/voice/gather",
            method="POST",
            language="en-US"
        )
        
        response.say("I'm still having trouble hearing you. Please call back when you can speak more clearly.", voice="alice")
        response.hangup()
        
        return response
    
    def _create_error_response(self) -> VoiceResponse:
        """Create error response for system failures"""
        response = VoiceResponse()
        
        response.say(
            "I'm sorry, there's a technical issue with our system right now. "
            "If this is an emergency, please hang up and call 911 immediately. "
            "Otherwise, try calling back in a few minutes.",
            voice="alice"
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