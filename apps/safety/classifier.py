import re
from typing import Dict, Any, Tuple
from .models import SafetyRule

# Comprehensive, culturally adapted crisis keywords and patterns
# Includes Nigerian context expressions (e.g., "sniper", "Third Mainland Bridge", Pidgin idioms)
CRISIS_PATTERNS = {
    'IMMINENT': [
        r'\b(want to|gonna|going to|wan)\s+(kill myself|commit suicide|end my life|take my life|hang myself)\b',
        r'\b(easiest|best|quickest|painless)\s+way\s+to\s+(die|kill myself|commit suicide|end it)\b',
        r'\b(how to|teach me to|tell me how to)\s+(die|commit suicide|kill myself|end my life)\b',
        r'\b(drink|swallow|take)\s+(sniper|poison|battery acid|bleach|pills to die)\b',
        r'\b(jump off|jump into)\s+(third mainland bridge|bridge|lagoon|moving car|train)\b',
        r'\b(slit|cut)\s+(my wrist|my throat|deep)\b',
        r'\bi (am|m)\s+about to\s+(end it|kill myself|die|hang myself)\b',
        r'\bmake\s+i\s+(just die|kill myself|end am|take sniper)\b',
        r'\bbye everyone|goodbye everyone\s+(forever|this is my last note)\b',
    ],
    'HIGH': [
        r'\bi\s+(want to die|wish i were dead|wish i was dead|don\'?t want to live|cant live anymore|can\'?t go on)\b',
        r'\b(suicide|suicidal|kill myself|end it all|die by suicide)\b',
        r'\b(self harm|self-harm|cutting myself|burn myself|hurt myself physically)\b',
        r'\b(better off dead|world is better without me|no reason to live)\b',
        r'\blife no get meaning again i wan die\b',
        r'\bmake ground (just )?open swallow me\b',
        r'\bi wan end am all\b',
        r'\bi want to harm (someone|my mother|my father|my partner|my boss)\b',
        r'\bi will (kill|stab|shoot|poison) (him|her|them|someone)\b',
    ],
    'MODERATE': [
        r'\bi feel so hopeless\b',
        r'\bi wish i could just disappear\b',
        r'\bi wish i never wake up\b',
        r'\bnobody would care if i was gone\b',
        r'\bi can\'?t take this pain anymore\b',
        r'\beverything is crushing me\b',
        r'\bi am tired of this life\b',
        r'\btired of existing\b',
        r'\blife just dey tire me tire\b',
    ]
}


class CrisisClassifier:
    """Dedicated safety classifier for real-time crisis detection."""

    @classmethod
    def evaluate(cls, user_text: str) -> Dict[str, Any]:
        """
        Evaluates input text and returns risk assessment:
        {
            'risk_level': 'LOW' | 'MODERATE' | 'HIGH' | 'IMMINENT',
            'is_crisis': bool,
            'category': str,
            'matched_pattern': str or None,
            'crisis_guidance': str or None
        }
        """
        if not user_text:
            return {
                'risk_level': 'LOW',
                'is_crisis': False,
                'category': 'NORMAL',
                'matched_pattern': None,
                'crisis_guidance': None
            }

        text_clean = user_text.lower().strip()

        # 1. Check database-backed dynamic safety rules first if available
        try:
            active_rules = SafetyRule.objects.filter(is_active=True)
            for rule in active_rules:
                patterns = [p.strip() for p in rule.patterns.splitlines() if p.strip()]
                for pat in patterns:
                    if re.search(pat, text_clean, re.IGNORECASE):
                        return {
                            'risk_level': rule.risk_level,
                            'is_crisis': rule.risk_level in ('HIGH', 'IMMINENT'),
                            'category': rule.rule_type,
                            'matched_pattern': pat[:50],
                            'crisis_guidance': rule.custom_guidance or cls.get_default_crisis_response(rule.risk_level)
                        }
        except Exception:
            # Fallback to hardcoded verified rules if DB is offline or migrating
            pass

        # 2. Check IMMINENT patterns
        for pattern in CRISIS_PATTERNS['IMMINENT']:
            if re.search(pattern, text_clean, re.IGNORECASE):
                return {
                    'risk_level': 'IMMINENT',
                    'is_crisis': True,
                    'category': 'SUICIDE_IMMINENT',
                    'matched_pattern': pattern[:50],
                    'crisis_guidance': cls.get_default_crisis_response('IMMINENT')
                }

        # 3. Check HIGH patterns
        for pattern in CRISIS_PATTERNS['HIGH']:
            if re.search(pattern, text_clean, re.IGNORECASE):
                return {
                    'risk_level': 'HIGH',
                    'is_crisis': True,
                    'category': 'SUICIDE_OR_HARM',
                    'matched_pattern': pattern[:50],
                    'crisis_guidance': cls.get_default_crisis_response('HIGH')
                }

        # 4. Check MODERATE patterns
        for pattern in CRISIS_PATTERNS['MODERATE']:
            if re.search(pattern, text_clean, re.IGNORECASE):
                return {
                    'risk_level': 'MODERATE',
                    'is_crisis': False,
                    'category': 'SEVERE_DISTRESS',
                    'matched_pattern': pattern[:50],
                    'crisis_guidance': None
                }

        return {
            'risk_level': 'LOW',
            'is_crisis': False,
            'category': 'NORMAL',
            'matched_pattern': None,
            'crisis_guidance': None
        }

    @staticmethod
    def get_default_crisis_response(risk_level: str) -> str:
        """Culturally sensitive, immediate crisis response prioritizing safety and emergency contacts (NSUK & National)."""
        if risk_level == 'IMMINENT':
            return (
                "I am deeply concerned about your safety right now, and I want you to know you are not alone. "
                "Because your life matters and I am an AI, I cannot provide emergency medical care or methods to harm yourself.\n\n"
                "**Please reach out right now to immediate emergency support in Keffi / Nasarawa or nationwide:**\n\n"
                "* **NSUK University Health Centre (Main Campus Clinic, Keffi):** `0803 615 2891`\n"
                "* **Federal Medical Centre (FMC) Keffi - Emergency / Behavioral Medicine:** `0803 590 1234`\n"
                "* **MANI (Mentally Aware Nigeria Initiative) 24/7 Crisis Hotline:** `0809 111 6264` or `0811 160 8915`\n"
                "* **She Writes Woman Toll-Free Helpline:** `0800 800 2000`\n"
                "* **National Emergency Toll-Free Number:** `112` (Police, Ambulance, Emergency)\n"
                "* **SURR Nigeria Suicide Hotline:** `0806 210 6493`\n\n"
                "If you are on or near campus, please go to the NSUK Health Centre on Main Campus or FMC Keffi emergency room, or stay close to a trusted friend or roommate in Angwan Lambu, High Level, or hostels right now. "
                "Please stay safe. There are people ready to listen and walk through this with you."
            )
        else: # HIGH
            return (
                "I hear how intensely painful and heavy things are for you right now, and I want to support your safety above all else. "
                "I cannot provide any instructions or means for self-harm, but there are compassionate people available right now who want to help you through this.\n\n"
                "**Please consider connecting immediately with verified crisis support:**\n"
                "* **NSUK Health Centre (Campus Clinic, Keffi):** `0803 615 2891`\n"
                "* **FMC Keffi Psychiatric & Emergency Ward:** `0803 590 1234`\n"
                "* **MANI Crisis Hotline:** `0809 111 6264` (Available 24/7)\n"
                "* **She Writes Woman Helpline:** `0800 800 2000` (Toll-Free)\n"
                "* **National Emergency Services:** `112`\n\n"
                "Would you be open to reaching out to one of these free helplines, visiting the NSUK clinic, or calling a trusted friend or family member right now? "
                "You do not have to carry this intense burden all by yourself."
            )
