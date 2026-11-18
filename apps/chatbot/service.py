import logging
from typing import Dict, Any, List
from django.utils.html import escape
from apps.safety.classifier import CrisisClassifier
from apps.safety.validator import OutputSafetyValidator
from apps.safety.models import SafetyEvent
from .ai_client import LLMClient
from .prompts import build_system_prompt

logger = logging.getLogger(__name__)

class ChatbotSafetyPipeline:
    """
    AI Safety Middleware pipeline implementing Section 18:
    User Message -> Input Validation -> Safety/Crisis Detection ->
    Cultural Context Detection -> AI Model -> Output Safety Validation -> Safe Response
    """

    def __init__(self):
        self.llm_client = LLMClient()

    def process_message(
        self,
        user_message: str,
        user=None,
        conversation_history: List[Dict[str, str]] = None,
        session_language: str = None,
        session_id: str = ''
    ) -> Dict[str, Any]:
        """
        Processes a user message through the full multi-tier safety pipeline.
        """
        # Step 1: Input Validation
        if not user_message or not user_message.strip():
            return {
                'content': "I'm here whenever you're ready to share. How are you feeling right now?",
                'risk_level': 'LOW',
                'is_crisis': False,
                'category': 'NORMAL'
            }

        cleaned_text = user_message.strip()
        if len(cleaned_text) > 4000:
            cleaned_text = cleaned_text[:4000]

        # Step 2: Safety & Crisis Detection (Pre-generation)
        safety_eval = CrisisClassifier.evaluate(cleaned_text)
        risk_level = safety_eval['risk_level']
        is_crisis = safety_eval['is_crisis']
        category = safety_eval['category']

        # Log safety events for non-low risks
        if risk_level in ('MODERATE', 'HIGH', 'IMMINENT'):
            try:
                SafetyEvent.objects.create(
                    user=user if user and user.is_authenticated else None,
                    risk_level=risk_level,
                    category=category,
                    matched_pattern_sanitized=safety_eval.get('matched_pattern') or 'Keyword rule',
                    intervention_taken='Provided verified Nigerian emergency crisis contacts' if is_crisis else 'Triggered supportive inquiry',
                    location_state=getattr(user, 'state_region', '') if user and user.is_authenticated else '',
                    session_id=session_id
                )
            except Exception as e:
                logger.error(f"Failed to record SafetyEvent: {e}")

        # If crisis is IMMINENT or HIGH, intercept immediately with verified crisis resources
        if is_crisis:
            crisis_response = safety_eval.get('crisis_guidance') or CrisisClassifier.get_default_crisis_response(risk_level)
            return {
                'content': crisis_response,
                'risk_level': risk_level,
                'is_crisis': True,
                'category': category
            }

        # Step 3: Cultural Context Detection & Prompt Construction
        system_prompt = build_system_prompt(user=user, session_language=session_language)

        messages_payload = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            # Include up to the last 10 messages for conversation continuity
            for msg in conversation_history[-10:]:
                messages_payload.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages_payload.append({"role": "user", "content": cleaned_text})

        # Step 4: AI Model Generation
        raw_ai_response = self.llm_client.generate_chat_completion(
            messages=messages_payload,
            temperature=0.7,
            max_tokens=650
        )

        # Step 5: Output Safety Validation
        is_safe, reason, final_content = OutputSafetyValidator.validate(raw_ai_response)
        if not is_safe:
            logger.warning(f"Output safety triggered: {reason}")

        return {
            'content': final_content,
            'risk_level': risk_level,
            'is_crisis': False,
            'category': category,
            'safety_reason': reason
        }
