"""Default seed coping exercises with Nigerian context nuances."""

DEFAULT_COPING_TOOLS = [
    {
        'slug': 'box-breathing',
        'title': 'Box Breathing (Samavritti)',
        'category': 'breathing',
        'short_description': 'Calm your autonomic nervous system with a balanced 4-second cycle.',
        'duration_minutes': 4,
        'icon': 'bi-wind',
        'overview': 'Box breathing is a powerful, discreet stress-relief practice used to quickly bring your heart rate down and clear mental fog when feeling overloaded.',
        'is_interactive': True,
        'order': 1,
        'steps': [
            {'title': 'Inhale', 'instruction': 'Breathe in slowly and deeply through your nose for 4 counts.', 'hint': 'Feel your lungs expanding with calm energy.'},
            {'title': 'Hold', 'instruction': 'Gently hold your breath for 4 counts.', 'hint': 'Do not clamp tightly; just be still.'},
            {'title': 'Exhale', 'instruction': 'Release the breath smoothly through your mouth for 4 counts.', 'hint': 'Let tension in your shoulders drop.'},
            {'title': 'Hold', 'instruction': 'Wait in the stillness for 4 counts before repeating the cycle.', 'hint': 'Feel steady in this moment.'}
        ]
    },
    {
        'slug': 'grounding-54321',
        'title': '5-4-3-2-1 Sensory Grounding',
        'category': 'grounding',
        'short_description': 'Anchor yourself in the present moment when feeling anxious or detached.',
        'duration_minutes': 5,
        'icon': 'bi-eye',
        'overview': 'When anxiety pulls your thoughts into past regrets or future panic, this sensory countdown gently returns your focus to the immediate physical room.',
        'is_interactive': True,
        'order': 2,
        'steps': [
            {'title': '5 Things You Can SEE', 'instruction': 'Look around your room. Notice 5 distinct objects (a book, a shadow, a pen, the doorway, a fabric).', 'hint': 'Pay attention to shapes and colors.'},
            {'title': '4 Things You Can TOUCH', 'instruction': 'Notice 4 physical textures (your sleeve, the wooden desk, your phone screen, the floor beneath your feet).', 'hint': 'Notice warmth, roughness, or coolness.'},
            {'title': '3 Things You Can HEAR', 'instruction': 'Tune in to 3 ambient sounds around you (generator humming, car horns outside, a fan whirring, birds).', 'hint': 'Listen without judging the noise.'},
            {'title': '2 Things You Can SMELL', 'instruction': 'Notice 2 scents in the air (rain on dust, food cooking, lotion, or clean laundry).', 'hint': 'Take a gentle sniff.'},
            {'title': '1 Thing You Can TASTE', 'instruction': 'Notice the current taste in your mouth, or take a sip of cool drinking water.', 'hint': 'Notice the temperature and feeling.'}
        ]
    },
    {
        'slug': 'progressive-muscle-relaxation',
        'title': 'Progressive Muscle Relaxation (PMR)',
        'category': 'mindfulness',
        'short_description': 'Systematically release physical tightness held in your neck, back, and shoulders.',
        'duration_minutes': 8,
        'icon': 'bi-person-arms-up',
        'overview': 'Physical stress accumulates in muscles without our conscious knowledge. PMR teaches your body the contrast between clenched tension and deep physical ease.',
        'is_interactive': True,
        'order': 3,
        'steps': [
            {'title': 'Forehead & Brow', 'instruction': 'Squeeze your facial muscles and frown tightly for 5 seconds... then completely let go and breathe out.', 'hint': 'Feel your forehead smooth out.'},
            {'title': 'Jaw & Teeth', 'instruction': 'Gently clench your jaw for 5 seconds without straining... now release and let your mouth part naturally.', 'hint': 'Notice the heavy release in your cheeks.'},
            {'title': 'Shoulders & Neck', 'instruction': 'Hunch your shoulders up towards your ears for 5 seconds... then drop them completely down.', 'hint': 'Imagine a heavy weight lifting off you.'},
            {'title': 'Hands & Forearms', 'instruction': 'Make tight fists with both hands for 5 seconds... then open your fingers wide and relax them on your lap.', 'hint': 'Feel the tingling warmth return.'},
            {'title': 'Feet & Calves', 'instruction': 'Point your toes upward and tighten your calves for 5 seconds... then release them into the floor.', 'hint': 'Sink gently into your seat.'}
        ]
    },
    {
        'slug': 'academic-burnout-planner',
        'title': 'NSUK Semester & Exam Burnout Reset',
        'category': 'academic',
        'short_description': 'Overcome overwhelm from continuous assessments (CA), semester exams, and carry-over fears.',
        'duration_minutes': 6,
        'icon': 'bi-journal-bookmark',
        'overview': 'Designed specifically for students at Nasarawa State University Keffi (NSUK) navigating intense lecture schedules, library revision sessions, CA tests, and high expectations from loved ones.',
        'is_interactive': True,
        'order': 4,
        'steps': [
            {'title': 'Step 1: The Brain Dump', 'instruction': 'Write down every single school obligation (assignments, practical reports, test preparation) on a single sheet of paper without judging yourself.', 'hint': 'Emptying your mind reduces cognitive fatigue.'},
            {'title': 'Step 2: Choose Just One 15-Minute Task', 'instruction': 'Pick the single smallest, easiest 15-minute task from your list (e.g. read two lecture slides or review one past question). Ignore the rest for now.', 'hint': 'Action creates motivation, not the other way around.'},
            {'title': 'Step 3: Work in 25-Minute Blocks (Pomodoro)', 'instruction': 'Set a timer for 25 minutes. Study with zero WhatsApp or phone notifications.', 'hint': 'Short sprints protect your focus in the heat.'},
            {'title': 'Step 4: Mandatory 5-Minute Cooldown & Hydration', 'instruction': 'Step away from your desk, stretch your neck and shoulders, drink cold water. If feeling panic, remind yourself: A test score does not measure your full human dignity.', 'hint': 'Take a breath. You are capable of navigating this semester.'}
        ]
    },
    {
        'slug': 'sleep-hygiene-nigeria',
        'title': 'Rest & Sleep in Keffi Hostels (Angwan Lambu / High Level)',
        'category': 'sleep',
        'short_description': 'Practical strategies to rest better despite Keffi room heat, generator humming, and roommate noise.',
        'duration_minutes': 5,
        'icon': 'bi-moon-stars',
        'overview': 'Sleeping well while staying off-campus around Keffi (Angwan Lambu, High Level, Total) or campus hostels often involves generator noise, room warmth, and exam anxiety. Here are evidence-informed adjustments to maximize your restorative rest.',
        'is_interactive': True,
        'order': 5,
        'steps': [
            {'title': 'Sound Cushioning', 'instruction': 'If generator noise around your compound is relentless, use earplugs or play rhythmic low rain sounds to mask sudden harsh spikes in sound.', 'hint': 'A steady low drone is easier for the brain to tune out.'},
            {'title': 'Cool Down Protocol', 'instruction': 'Take a quick lukewarm or cool shower right before lying down to trigger your core body temperature to drop, which induces sleepiness even in warm Keffi weather.', 'hint': 'Wear loose, breathable cotton.'},
            {'title': 'The Worry Notepad', 'instruction': 'Keep a notebook beside your bed. If thoughts about school fees, rent, or tomorrow\'s test spin in your head, write them down so your brain knows they are recorded.', 'hint': 'You cannot resolve tomorrow\'s challenges at midnight.'},
            {'title': 'Digital Sunset', 'instruction': 'Put your smartphone down at least 30 minutes before sleep. Blue screen light fools your brain into thinking it is midday.', 'hint': 'Allow your eyes to rest in darkness.'}
        ]
    },
    {
        'slug': 'gratitude-and-reflection',
        'title': 'Grounded Reflection & Gratitude',
        'category': 'journaling',
        'short_description': 'Nurture resilience by acknowledging what is steady, without denying real difficulties.',
        'duration_minutes': 7,
        'icon': 'bi-chat-heart',
        'overview': 'Gratitude is not toxic positivity or ignoring pain. It is giving equal airtime to the small mercies, kind people, and strengths that have carried you this far.',
        'is_interactive': True,
        'order': 6,
        'steps': [
            {'title': 'One Simple Comfort', 'instruction': 'Name one small physical thing you had today that gave you comfort (a hot meal, a cold drink, shade, a warm shower).', 'hint': 'Small things count.'},
            {'title': 'One Person or Voice', 'instruction': 'Think of one person (friend, mentor, sibling, or community member) who showed you kindness recently.', 'hint': 'Feel the warmth of that connection.'},
            {'title': 'One Strength in Yourself', 'instruction': 'Acknowledge one difficulty you faced in the past that you survived and navigated.', 'hint': 'You are more resilient than you often give yourself credit for.'}
        ]
    }
]
