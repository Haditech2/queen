import os
import json
import time
import logging
import requests
from django.conf import settings
from typing import List, Dict, Any, Generator

logger = logging.getLogger(__name__)

# Total seconds a user may wait for Gemini before we use the offline fallback,
# and the longest a single model attempt may take.
GEMINI_TOTAL_BUDGET_SECONDS = 45
GEMINI_PER_CALL_TIMEOUT_SECONDS = 15


class LLMClient:
    # Remembers the last Gemini model that answered, so later messages try it first
    # instead of waiting on overloaded/unavailable models again.
    _last_working_gemini_model = None

    """
    Unified LLM Client abstraction supporting:
    - Google Gemini API (gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash)
    - NVIDIA API (e.g. deepseek-ai/deepseek-v4.1-flash, llama-3.1-70b-instruct)
    - DeepSeek (deepseek-chat)
    - Kimi (moonshot-v1-8k)
    - GLM (glm-4)
    - OpenAI (gpt-4o, gpt-4o-mini)
    """

    def __init__(self):
        self.provider = getattr(settings, 'AI_PROVIDER', os.getenv('AI_PROVIDER', 'gemini')).lower()
        # Keys come only from Django settings (which already load .env), so tests and
        # deployments can override them in one place.
        gemini_key = getattr(settings, 'GEMINI_API_KEY', '') or ''
        generic_key = getattr(settings, 'AI_API_KEY', '') or ''
        if self.provider == 'gemini':
            self.api_key = (gemini_key or generic_key).strip()
        else:
            self.api_key = (generic_key or gemini_key).strip()

        if self.provider == 'gemini':
            cfg_model = getattr(settings, 'AI_MODEL', None) or os.getenv('AI_MODEL', '')
            self.model = cfg_model if (cfg_model and 'gemini' in cfg_model.lower()) else 'gemini-3.6-flash'
            cfg_url = getattr(settings, 'AI_BASE_URL', None) or os.getenv('AI_BASE_URL', '')
            self.base_url = (cfg_url if (cfg_url and 'googleapis' in cfg_url) else 'https://generativelanguage.googleapis.com/v1beta/openai').rstrip('/')
        else:
            self.model = getattr(settings, 'AI_MODEL', os.getenv('AI_MODEL', 'deepseek-ai/deepseek-v4.1-flash'))
            self.base_url = getattr(
                settings, 'AI_BASE_URL',
                os.getenv('AI_BASE_URL', 'https://integrate.api.nvidia.com/v1')
            ).rstrip('/')

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 800,
        timeout: int = 40
    ) -> str:
        """
        Sends conversation messages to configured LLM API (Gemini or OpenAI-compatible).
        """
        # If no API key configured, use high-fidelity culturally adapted fallback engine
        if not self.api_key:
            logger.info("MindBridge: No AI_API_KEY / GEMINI_API_KEY configured. Utilizing culturally adapted empathetic fallback.")
            return self._fallback_generate(messages)

        # 1. Primary path for Gemini: Call Google Gemini REST API directly
        if self.provider == 'gemini' or 'googleapis.com' in self.base_url:
            native_res = self._call_gemini_native(messages, temperature, max_tokens, timeout)
            if native_res:
                return native_res
            if self.provider == 'gemini':
                return self._fallback_generate(messages)

        # 2. Path for OpenAI-compatible gateways (NVIDIA, DeepSeek, OpenAI, etc.)
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "x-goog-api-key": self.api_key,  # For Google Gemini API gateways
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                return content.strip()
            else:
                logger.warning(f"Primary endpoint returned {resp.status_code}: {resp.text[:200]}")
                return self._fallback_generate(messages)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling LLM provider ({self.provider}): {e}")
            return self._fallback_generate(messages)

    def _call_gemini_native(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 800,
        timeout: int = 20
    ) -> str:
        """Direct call to Google Gemini native REST API with auto-fallback for active models."""
        candidate_models = []
        # Fast, highly available lite model goes second so a busy primary model never
        # leaves the user waiting through the whole list.
        for m in [LLMClient._last_working_gemini_model, self.model, 'gemini-3.1-flash-lite', 'gemini-3.6-flash', 'gemini-flash-latest', 'gemini-3.8-flash', 'gemini-3.7-flash', 'gemini-3.5-flash']:
            if m and m not in candidate_models:
                candidate_models.append(m)

        deadline = time.monotonic() + GEMINI_TOTAL_BUDGET_SECONDS
        for model_candidate in candidate_models:
            for attempt in range(2):
                remaining = deadline - time.monotonic()
                if remaining < 2:
                    logger.warning("Gemini time budget exhausted; using offline fallback reply.")
                    return ""
                call_timeout = min(timeout, GEMINI_PER_CALL_TIMEOUT_SECONDS, remaining)
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_candidate}:generateContent"
                    contents = []
                    system_instruction = ""
                    for m in messages:
                        role = m.get('role', 'user')
                        text = m.get('content', '')
                        if role == 'system':
                            system_instruction += text + "\n"
                        elif role == 'assistant':
                            contents.append({"role": "model", "parts": [{"text": text}]})
                        else:
                            contents.append({"role": "user", "parts": [{"text": text}]})

                    payload = {
                        "contents": contents,
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": max_tokens
                        }
                    }
                    if system_instruction.strip():
                        payload["systemInstruction"] = {"parts": [{"text": system_instruction.strip()}]}

                    resp = requests.post(
                        url,
                        headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
                        json=payload,
                        timeout=call_timeout,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get('candidates', [])
                        if candidates and 'content' in candidates[0]:
                            parts = candidates[0]['content'].get('parts', [])
                            if parts and 'text' in parts[0]:
                                logger.info(f"Gemini responded directly using model {model_candidate}")
                                LLMClient._last_working_gemini_model = model_candidate
                                return parts[0]['text'].strip()
                    elif resp.status_code == 503 and attempt == 0:
                        time.sleep(0.8)
                        continue
                    else:
                        logger.warning(f"Gemini native API ({model_candidate}) returned {resp.status_code}: {resp.text[:120]}")
                        break
                except Exception as e:
                    logger.error(f"Gemini native call error on {model_candidate}: {e}")
                    break
        return ""

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> Generator[str, None, None]:
        """
        Streams response chunks using Server-Sent Events (SSE).
        """
        if not self.api_key:
            full_text = self._fallback_generate(messages)
            words = full_text.split(" ")
            for i in range(0, len(words), 3):
                yield " ".join(words[i:i+3]) + " "
            return

        if self.provider == 'gemini' or 'googleapis.com' in self.base_url:
            direct_reply = self._call_gemini_native(messages, temperature, max_tokens)
            if direct_reply:
                words = direct_reply.split(" ")
                for i in range(0, len(words), 3):
                    yield " ".join(words[i:i+3]) + " "
                return

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "x-goog-api-key": self.api_key,
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        try:
            with requests.post(endpoint, headers=headers, json=payload, stream=True, timeout=45) as resp:
                if resp.status_code == 200:
                    for line in resp.iter_lines():
                        if line:
                            decoded = line.decode('utf-8')
                            if decoded.startswith('data: '):
                                json_part = decoded[6:].strip()
                                if json_part == '[DONE]':
                                    break
                                try:
                                    chunk_data = json.loads(json_part)
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                                except Exception:
                                    continue
                else:
                    yield self._fallback_generate(messages)
        except Exception as e:
            logger.error(f"Streaming error calling LLM provider: {e}")
            yield self._fallback_generate(messages)

    def _fallback_generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Culturally nuanced, empathetic response generation for offline/demo/keyless mode.
        Complies strictly with Section 6, 7, 8, and 19.
        """
        last_user_msg = ""
        for m in reversed(messages):
            if m.get('role') == 'user':
                last_user_msg = m.get('content', '')
                break

        text_lower = last_user_msg.lower()

        # Pidgin check
        if any(w in text_lower for w in ['dey', 'wetin', 'abi', 'na wa', 'fit', 'sabi', 'wahala', 'baffled', 'no get']):
            if 'school' in text_lower or 'exam' in text_lower or 'read' in text_lower:
                return (
                    "I hear you well. Academic stress fit really weigh person down, especially when exams dey come and expectations high. "
                    "You don try your best, but body no be firewood. Which part dey worry you pass right now — the workload, time, or the pressure from home?"
                )
            if 'money' in text_lower or 'work' in text_lower or 'job' in text_lower or 'cash' in text_lower:
                return (
                    "I hear you loud and clear. Financial pressure and hustle for this country fit really drain person mentally. "
                    "It is completely valid to feel overwhelmed by all the responsibilities. Would you like to take a deep breath together, or talk about what is feeling most urgent today?"
                )
            return (
                "I hear you. E sounds like things have been really heavy and overwhelming lately. "
                "You don't have to carry everything all at once. Which part feels heaviest on your mind right now?"
            )

        # NSUK Campus Living & Keffi Environment
        if any(w in text_lower for w in ['angwan lambu', 'high level', 'hostel', 'keffi', 'total junction', 'generator', 'heat', 'roommate', 'shuttle']):
            return (
                "Living around Keffi — whether navigating off-campus life in Angwan Lambu, High Level, or on-campus hostels with room heat and power outages — can take a heavy toll on your daily stamina. "
                "It is completely valid that you are feeling physically and mentally drained right now. "
                "Are you in a spot where you can pause for a few minutes and take a cool drink of water together?"
            )

        # Academic / school / NSUK semester stress
        if any(w in text_lower for w in ['school', 'exam', 'university', 'jamb', 'lecturer', 'grades', 'academic', 'carryover', 'spillover', 'clearance', 'faculty', 'cgpa', 'ca']):
            return (
                "That sounds exhausting, especially when semester expectations and academic pressure at NSUK start affecting your sleep and peace of mind. "
                "What has been weighing on you most — upcoming exams, continuous assessments, carry-over worries, project deadlines, or the pressure from family back home?"
            )

        # Family / Relationship pressure
        if any(w in text_lower for w in ['family', 'parents', 'father', 'mother', 'marriage', 'pressure', 'expectations', 'relatives']):
            return (
                "Navigating family expectations can feel deeply draining, especially when you carry high hopes and personal boundaries at the same time. "
                "Some people in similar situations find that having a dedicated space to process those feelings can offer relief. "
                "How have you been trying to manage that balance so far?"
            )

        # Work / Financial / Unemployment stress
        if any(w in text_lower for w in ['job', 'unemployment', 'money', 'bills', 'broke', 'career', 'economy', 'workplace']):
            return (
                "Financial strain and work uncertainty carry a very real emotional toll, especially in times of economic hardship. "
                "It takes a lot of mental energy just to keep pushing each day. "
                "What has helped you stay grounded even a little bit during previous tough seasons?"
            )

        # Grief / Loss
        if any(w in text_lower for w in ['lost', 'died', 'passed away', 'grief', 'death', 'mourning']):
            return (
                "I want to sit with you in this moment. Grieving someone you care about can feel disorienting and deeply exhausting, with emotions coming in waves. "
                "There is no timeline or 'correct' way to feel right now. Do you have a trusted person or community you feel safe resting around today?"
            )

        # Default supportive response
        return (
            "I hear what you are saying, and I appreciate you sharing that with me. "
            "When life feels complex or heavy, acknowledging it is often the first gentle step. "
            "Would you like to unpack what's been happening a bit more, or would you prefer to try a quick calming coping exercise together?"
        )
