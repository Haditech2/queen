"""
Validated Clinical Screening Questions & Scoring Matrices.
Non-diagnostic: Intended for self-reflection and guidance on when to seek professional consultation.
"""

COMMON_SCALE_0_TO_3 = [
    {"value": 0, "label": "Not at all"},
    {"value": 1, "label": "Several days"},
    {"value": 2, "label": "More than half the days"},
    {"value": 3, "label": "Nearly every day"},
]

QUESTIONNAIRE_DEFINITIONS = {
    'PHQ2': {
        'name': 'PHQ-2 (Brief Depression Screener)',
        'description': 'A two-item screening tool to measure frequency of depressed mood and loss of interest over the last two weeks.',
        'instructions': 'Over the last 2 weeks, how often have you been bothered by any of the following problems?',
        'options': COMMON_SCALE_0_TO_3,
        'questions': [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
        ],
        'scoring': lambda score: (
            ("Screening Suggests Further Evaluation", "A score of 3 or higher on the PHQ-2 suggests that further evaluation with a full questionnaire (such as the PHQ-9) or a conversation with a qualified mental health healthcare provider may be very helpful.")
            if score >= 3 else
            ("Within Typical Screening Range", "Your responses fall within the lower range on this initial screener. However, if you are still feeling persistently stressed or low, please consider speaking with a trusted professional or using the coping toolkit.")
        )
    },
    'PHQ9': {
        'name': 'PHQ-9 (Patient Health Questionnaire - 9)',
        'description': 'A 9-question tool that screens for the presence and severity of depressive symptoms over the past two weeks.',
        'instructions': 'Over the last 2 weeks, how often have you been bothered by any of the following problems?',
        'options': COMMON_SCALE_0_TO_3,
        'questions': [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading or watching television",
            "Moving or speaking so slowly that other people could have noticed, or being so fidgety/restless that you have been moving around much more than usual",
            "Thoughts that you would be better off dead or of hurting yourself in some way",
        ],
        'scoring': lambda score: (
            ("Minimal / Low Symptoms", "Your score indicates minimal depressive symptoms. Continue caring for your physical, emotional, and social wellbeing.") if score <= 4 else
            ("Mild Symptoms", "Your score suggests mild symptoms. Practicing evidence-based coping exercises, connecting with trusted loved ones, and monitoring your mood may be beneficial.") if score <= 9 else
            ("Moderate Symptoms", "Your score suggests moderate symptoms. Consulting with a licensed mental health professional (such as a counselor or clinical psychologist) is strongly recommended for guidance.") if score <= 14 else
            ("Moderately Severe Symptoms", "Your score suggests moderately severe symptoms. We encourage you to reach out to a healthcare professional or verified mental health clinic for an assessment and individualized support plan.") if score <= 19 else
            ("Severe Symptoms", "Your score suggests severe symptoms. Please prioritize connecting with a qualified doctor, clinical psychologist, psychiatrist, or one of our verified Nigerian crisis resources immediately.")
        )
    },
    'GAD2': {
        'name': 'GAD-2 (Brief Anxiety Screener)',
        'description': 'A two-item screening instrument used to identify potential generalized anxiety concerns.',
        'instructions': 'Over the last 2 weeks, how often have you been bothered by the following problems?',
        'options': COMMON_SCALE_0_TO_3,
        'questions': [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
        ],
        'scoring': lambda score: (
            ("Elevated Anxiety Screening", "A score of 3 or higher suggests exploring this further with the GAD-7 assessment or scheduling a conversation with a qualified mental health specialist.")
            if score >= 3 else
            ("Within Typical Screening Range", "Your responses indicate minimal reported anxiety symptoms over the past fortnight.")
        )
    },
    'GAD7': {
        'name': 'GAD-7 (Generalized Anxiety Disorder - 7)',
        'description': 'A 7-item questionnaire designed to screen for and measure the severity of generalized anxiety symptoms.',
        'instructions': 'Over the last 2 weeks, how often have you been bothered by the following problems?',
        'options': COMMON_SCALE_0_TO_3,
        'questions': [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it is hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid, as if something awful might happen",
        ],
        'scoring': lambda score: (
            ("Minimal Anxiety", "Your score reflects minimal anxiety symptoms. Keep utilizing positive coping strategies to maintain your balance.") if score <= 4 else
            ("Mild Anxiety", "Your score reflects mild anxiety symptoms. Mindfulness, breathing exercises, and journaling can help reduce tension.") if score <= 9 else
            ("Moderate Anxiety", "Your score reflects moderate anxiety symptoms. Speaking with a counselor or therapist is recommended to explore coping mechanisms.") if score <= 14 else
            ("Severe Anxiety", "Your score reflects severe anxiety symptoms. Reaching out to a healthcare professional or local mental health specialist is strongly advised to support your wellbeing.")
        )
    }
}
