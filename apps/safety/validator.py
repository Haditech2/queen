import re
from typing import Tuple

class OutputSafetyValidator:
    """
    Validates LLM-generated responses before they reach the user.
    Prevents medical diagnoses, drug prescriptions, stereotyping, and unsafe content.
    """

    DIAGNOSIS_PATTERNS = [
        r'\b(you have|you suffer from|you are suffering from)\s+(clinical depression|major depressive disorder|bipolar|schizophrenia|an anxiety disorder|borderline personality)\b',
        r'\bi (diagnose|have diagnosed) you with\b',
        r'\bmy diagnosis is\b',
        r'\byour diagnosis is\b',
        r'\bas your (doctor|therapist|psychiatrist|psychologist)\b',
    ]

    PRESCRIPTION_PATTERNS = [
        r'\b(take|prescribe|administer|swallow)\s+\d+\s*(mg|milligrams|tablets|pills)\b',
        r'\b(sertraline|fluoxetine|escitalopram|alprazolam|diazepam|lexapro|prozac|zoloft|xanax|valium)\s+\d+\s*mg\b',
        r'\bi recommend you take (prozac|xanax|zoloft|lexapro|valium|sleeping pills)\b',
        r'\byou should start taking medication\b',
    ]

    STEREOTYPE_PATTERNS = [
        r'\bnigerians usually\b',
        r'\bafricans believe\b',
        r'\byour culture means that you\b',
        r'\ball nigerian parents\b',
        r'\bas an african you should\b',
    ]

    HARM_METHODS_PATTERNS = [
        r'\bhere is how you can (kill yourself|end your life|commit suicide|cut yourself)\b',
        r'\bto commit suicide, you can\b',
        r'\blethal dose of\b',
        r'\bways to die painless\b',
    ]

    @classmethod
    def validate(cls, text: str) -> Tuple[bool, str, str]:
        """
        Returns (is_safe: bool, reason: str, sanitized_or_fallback: str)
        """
        if not text:
            return True, "EMPTY", text

        text_lower = text.lower()

        # Check self-harm or lethal instructions
        for pat in cls.HARM_METHODS_PATTERNS:
            if re.search(pat, text_lower):
                return False, "HARM_INSTRUCTION", (
                    "I want to make sure you stay safe. I cannot provide instructions or methods that cause harm. "
                    "If you are going through an intense time, please call the MANI crisis line at 0809 111 6264 or She Writes Woman at 0800 800 2000."
                )

        # Check prescription / dosage
        for pat in cls.PRESCRIPTION_PATTERNS:
            if re.search(pat, text_lower):
                return False, "PRESCRIPTION_CLAIM", (
                    "I want to share that any decisions regarding medication or prescriptions must be made directly with a licensed medical doctor or psychiatrist. "
                    "Would you like help looking up verified medical and psychiatric centers in your area?"
                )

        # Check diagnosis claims
        for pat in cls.DIAGNOSIS_PATTERNS:
            if re.search(pat, text_lower):
                # Replace with non-diagnostic wording
                sanitized = re.sub(
                    r'\b(you have|you suffer from|you are suffering from)\s+(clinical depression|major depressive disorder|bipolar|schizophrenia|an anxiety disorder|borderline personality)\b',
                    'some people experiencing similar symptoms find it helpful to explore these feelings with a professional who can assess them properly',
                    text,
                    flags=re.IGNORECASE
                )
                return True, "DIAGNOSIS_SANITIZED", sanitized

        # Check cultural stereotypes
        for pat in cls.STEREOTYPE_PATTERNS:
            if re.search(pat, text_lower):
                sanitized = re.sub(r'\b(nigerians usually|africans believe)\b', 'some people in similar communities find', text, flags=re.IGNORECASE)
                return True, "STEREOTYPE_SANITIZED", sanitized

        return True, "CLEAN", text
