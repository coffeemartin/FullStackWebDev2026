"""Exercise recommendation helper.

Returns a structured plan for the Exercise page based on the user's BMI
and self-reported activity level.

The returned dict has the shape:
    {
        "label":      str,
        "focus":      str,
        "message":    str,
        "categories": list[str],
        "exercises":  list[dict],  # media-ready exercise cards for the UI
    }
"""

from typing import Optional


def _bmi_category(bmi: float) -> str:
    """Map a BMI number to one of four buckets used internally."""
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    return "obese"


def _normalize_level(level: Optional[str]) -> str:
    """Accept whatever the rest of the app stores and squash to 3 keys."""
    if not level:
        return "beginner"
    key = str(level).strip().lower()
    if key in {"beginner", "low", "sedentary", "easy", "lightly active"}:
        return "beginner"
    if key in {"intermediate", "moderate", "medium", "moderately active"}:
        return "intermediate"
    if key in {"advanced", "high", "hard", "expert", "very active"}:
        return "advanced"
    return "beginner"



_BMI_PROFILES = {
    "underweight": {
        "label": "Underweight",
        "focus": "Build healthy muscle and weight with calorie-supported strength work.",
        "message": "These categories help you gain strength steadily without overtraining.",
        "categories": ["Strength", "Mobility", "Light Cardio", "Recovery"],
    },
    "normal": {
        "label": "Healthy Range",
        "focus": "Maintain fitness with a balanced mix of strength and cardio.",
        "message": "A well-rounded routine to keep you progressing and feeling great.",
        "categories": ["Strength", "Cardio", "Mobility", "Skill / Sport"],
    },
    "overweight": {
        "label": "Overweight",
        "focus": "Improve cardiovascular health and start gentle strength training.",
        "message": "Lower-impact options to build a habit and protect your joints.",
        "categories": ["Low-Impact Cardio", "Strength", "Mobility", "Recovery"],
    },
    "obese": {
        "label": "Obese",
        "focus": "Prioritise low-impact movement, joint care, and gradual consistency.",
        "message": "Start small and stay consistent — these categories are joint-friendly.",
        "categories": ["Walking / Cycling", "Water-Based Cardio", "Mobility", "Recovery"],
    },
}


_EXERCISES = {
    "underweight": [
        {
            "name": "Goblet Squat",
            "video_embed": "https://www.youtube.com/embed/MeIiIdhvXT4",
            "category": "Strength",
            "benefit": "Builds leg and glute strength while teaching squat control.",
            "target": "Quadriceps, glutes, core",
            "equipment": "One dumbbell or kettlebell",
            "steps": [
                "Hold the weight close to your chest with elbows tucked in.",
                "Stand with feet shoulder-width apart and brace your core.",
                "Lower into a squat while keeping your chest lifted.",
                "Drive through your heels to stand back up.",
            ],
            "form_tip": "Keep your knees tracking over your toes instead of collapsing inward.",
            "easier_option": "Bodyweight squat to a chair.",
            "tips": {
                "beginner": "3 sets of 8 reps with a light weight.",
                "intermediate": "4 sets of 10 reps with a moderate load.",
                "advanced": "5 sets of 8 reps with a slow lowering phase.",
            },
        },
        {
            "name": "Push-Up",
            "video_embed": "https://www.youtube.com/embed/IODxDxX7oi4",
            "category": "Strength",
            "benefit": "Develops upper-body pressing strength and trunk stability.",
            "target": "Chest, shoulders, triceps, core",
            "equipment": "None",
            "steps": [
                "Place your hands slightly wider than shoulder-width apart.",
                "Create a straight line from head to heels.",
                "Lower your chest with control until your elbows reach about 90 degrees.",
                "Push the floor away to return to the start.",
            ],
            "form_tip": "Keep your hips level and avoid letting your lower back sag.",
            "easier_option": "Wall push-up or incline push-up on a bench.",
            "tips": {
                "beginner": "3 sets of 6 to 8 reps using an incline if needed.",
                "intermediate": "4 sets of 10 reps with standard form.",
                "advanced": "4 sets of 12 reps with a pause at the bottom.",
            },
        },
        {
            "name": "Dumbbell Row",
            "video_embed": "https://www.youtube.com/embed/pYcpY20QaE8",
            "category": "Strength",
            "benefit": "Improves upper-back strength and posture.",
            "target": "Lats, rhomboids, biceps",
            "equipment": "Dumbbell and bench or sturdy support",
            "steps": [
                "Hinge at the hips and support one hand on a bench or chair.",
                "Let the dumbbell hang below your shoulder with a flat back.",
                "Pull the weight toward your hip, leading with your elbow.",
                "Lower the dumbbell slowly until your arm is straight again.",
            ],
            "form_tip": "Keep your torso still instead of twisting to lift the weight.",
            "easier_option": "Use a lighter dumbbell and shorten the range slightly.",
            "tips": {
                "beginner": "3 sets of 10 reps per side with a light weight.",
                "intermediate": "4 sets of 10 reps per side with moderate load.",
                "advanced": "5 sets of 8 reps per side with a controlled tempo.",
            },
        },
        {
            "name": "Easy Walk",
            "video_embed": "https://www.youtube.com/embed/OMuHf1wQIug",
            "category": "Light Cardio",
            "benefit": "Builds basic endurance without interfering with recovery.",
            "target": "Heart health, calves, glutes",
            "equipment": "Walking shoes",
            "steps": [
                "Stand tall with your shoulders relaxed and your gaze forward.",
                "Start at a comfortable pace you can maintain while breathing easily.",
                "Swing your arms naturally to help your walking rhythm.",
                "Finish with a gradual cool-down pace for a couple of minutes.",
            ],
            "form_tip": "Walk tall instead of leaning forward from the hips.",
            "easier_option": "Split the walk into two shorter sessions.",
            "tips": {
                "beginner": "20 minutes at an easy conversational pace.",
                "intermediate": "30 minutes with a slightly brisk pace.",
                "advanced": "40 minutes including light inclines.",
            },
        },
        {
            "name": "Cat-Cow Stretch",
            "video_embed": "https://www.youtube.com/embed/xyNwxiuERXc",
            "category": "Mobility",
            "benefit": "Improves spinal mobility and breathing rhythm.",
            "target": "Spine, shoulders, hips",
            "equipment": "Mat",
            "steps": [
                "Start on all fours with hands under shoulders and knees under hips.",
                "Inhale and arch your back gently while lifting your chest.",
                "Exhale and round your spine while tucking your chin.",
                "Move slowly between both positions with smooth breathing.",
            ],
            "form_tip": "Use your breath to guide the pace rather than rushing the movement.",
            "easier_option": "Perform seated spinal flexion and extension in a chair.",
            "tips": {
                "beginner": "8 slow reps focusing on control.",
                "intermediate": "10 deeper reps paired with steady breathing.",
                "advanced": "12 reps with an added pause at each end range.",
            },
        },
        {
            "name": "Foam Rolling",
            "video_embed": "https://www.youtube.com/embed/c0JRlrKJXPg",
            "category": "Recovery",
            "benefit": "Reduces stiffness and helps your muscles relax after training.",
            "target": "Quads, upper back, calves",
            "equipment": "Foam roller",
            "steps": [
                "Place the foam roller under the muscle group you want to target.",
                "Support some bodyweight with your hands or opposite leg.",
                "Roll slowly over the muscle instead of rushing back and forth.",
                "Pause for a breath on any tight spots that feel manageable.",
            ],
            "form_tip": "Aim for slow pressure, not pain; foam rolling should feel intense but controlled.",
            "easier_option": "Use a softer roller or reduce bodyweight on the roller.",
            "tips": {
                "beginner": "5 minutes focusing on quads and upper back.",
                "intermediate": "10 minutes full-body rolling.",
                "advanced": "15 minutes with targeted release work.",
            },
        },
    ],
    "normal": [
        {
            "name": "Back Squat",
            "video_embed": "https://www.youtube.com/embed/8PMjqgR8Wa8",
            "category": "Strength",
            "benefit": "Builds overall lower-body strength and power.",
            "target": "Quadriceps, glutes, core",
            "equipment": "Barbell and rack",
            "steps": [
                "Set the bar across your upper back and stand with feet shoulder-width apart.",
                "Brace your core and sit down and back into the squat.",
                "Lower until you reach a comfortable depth with your chest up.",
                "Drive through the floor to return to standing.",
            ],
            "form_tip": "Keep your ribs down and torso braced before each rep.",
            "easier_option": "Goblet squat with a dumbbell.",
            "tips": {
                "beginner": "3 sets of 10 reps with bodyweight or an empty bar.",
                "intermediate": "4 sets of 8 reps with a moderate load.",
                "advanced": "5 sets of 5 reps with a heavier load.",
            },
        },
        {
            "name": "Bench Press",
            "video_embed": "https://www.youtube.com/embed/4Y2ZdHCOXok",
            "category": "Strength",
            "benefit": "Improves horizontal pressing strength and upper-body control.",
            "target": "Chest, shoulders, triceps",
            "equipment": "Barbell or dumbbells and bench",
            "steps": [
                "Lie on the bench with your feet planted firmly on the floor.",
                "Grip the bar slightly wider than shoulders and pull your shoulder blades back.",
                "Lower the bar to your chest with control.",
                "Press back up until your arms are straight.",
            ],
            "form_tip": "Keep your wrists stacked and elbows moving under the bar.",
            "easier_option": "Dumbbell bench press or push-up.",
            "tips": {
                "beginner": "3 sets of 10 reps with light dumbbells or bar.",
                "intermediate": "4 sets of 8 reps with a moderate load.",
                "advanced": "5 sets of 5 reps with a controlled eccentric.",
            },
        },
        {
            "name": "Running",
            "video_embed": "https://www.youtube.com/embed/LnNse_AwPyE",
            "category": "Cardio",
            "benefit": "Builds aerobic fitness and lower-body endurance.",
            "target": "Heart, lungs, calves, glutes",
            "equipment": "Running shoes",
            "steps": [
                "Start with a brisk walk or easy jog warm-up.",
                "Keep your posture tall and land softly under your body.",
                "Find a sustainable pace where you can control your breathing.",
                "Cool down with a slower jog or walk at the end.",
            ],
            "form_tip": "Relax your shoulders and let your arms swing close to your body.",
            "easier_option": "Run-walk intervals.",
            "tips": {
                "beginner": "20 minutes of run-walk intervals.",
                "intermediate": "30 minutes of steady jogging.",
                "advanced": "40 minutes including tempo or interval work.",
            },
        },
        {
            "name": "Plank",
            "video_embed": "https://www.youtube.com/embed/mwlp75MS6Rg",
            "category": "Mobility",
            "benefit": "Builds anti-extension core strength and shoulder stability.",
            "target": "Core, shoulders, glutes",
            "equipment": "Mat",
            "steps": [
                "Place your forearms on the floor with elbows under shoulders.",
                "Extend your legs back and form a straight line from head to heels.",
                "Brace your core and squeeze your glutes gently.",
                "Hold the position while breathing steadily.",
            ],
            "form_tip": "Think about pulling your elbows toward your toes without moving them.",
            "easier_option": "High plank on a bench or incline.",
            "tips": {
                "beginner": "3 holds of 20 seconds.",
                "intermediate": "3 holds of 45 seconds.",
                "advanced": "3 holds of 75 seconds.",
            },
        },
        {
            "name": "Yoga Flow",
            "video_embed": "https://www.youtube.com/embed/4TLHLNX65-4",
            "category": "Mobility",
            "benefit": "Improves movement quality, balance, and flexibility.",
            "target": "Full body",
            "equipment": "Mat",
            "steps": [
                "Start with mountain pose and steady breathing.",
                "Move through a simple sequence such as forward fold, plank, cobra, and downward dog.",
                "Transition slowly and keep each movement controlled.",
                "Finish with a gentle stretch and a few calming breaths.",
            ],
            "form_tip": "Move with your breath instead of forcing range of motion.",
            "easier_option": "Shorter beginner flow with fewer transitions.",
            "tips": {
                "beginner": "15 minutes of a basic beginner sequence.",
                "intermediate": "30 minutes of a vinyasa-style flow.",
                "advanced": "45 minutes with longer holds and balance work.",
            },
        },
        {
            "name": "Recreational Sport",
            "category": "Skill / Sport",
            "benefit": "Keeps fitness engaging while improving agility and coordination.",
            "target": "Full body",
            "equipment": "Varies by sport",
            "steps": [
                "Choose a sport you enjoy such as badminton, basketball, or tennis.",
                "Warm up for a few minutes before starting.",
                "Play at a level that matches your current fitness and skill.",
                "Cool down and stretch after the session.",
            ],
            "form_tip": "Treat fun movement as training too; consistency matters more than perfection.",
            "easier_option": "Short social games instead of full matches.",
            "tips": {
                "beginner": "Play something fun once a week for 30 to 45 minutes.",
                "intermediate": "Aim for 60 to 90 minutes of active play.",
                "advanced": "Mix gameplay with extra footwork or conditioning drills.",
            },
        },
    ],
    "overweight": [
        {
            "name": "Brisk Walking",
            "video_embed": "https://www.youtube.com/embed/OMuHf1wQIug",
            "category": "Low-Impact Cardio",
            "benefit": "Supports fat loss and stamina without heavy joint impact.",
            "target": "Heart health, calves, glutes",
            "equipment": "Walking shoes",
            "steps": [
                "Walk tall with your chest open and shoulders relaxed.",
                "Set a brisk pace where talking is possible but effort is noticeable.",
                "Use natural arm swing to keep momentum steady.",
                "Finish with a slower cool-down pace.",
            ],
            "form_tip": "Think about quick light steps rather than long heavy strides.",
            "easier_option": "Start with shorter 10 to 15 minute walks.",
            "tips": {
                "beginner": "20 minutes, 3 to 4 days each week.",
                "intermediate": "40 minutes daily at a brisk pace.",
                "advanced": "60 minutes with gentle hill intervals.",
            },
        },
        {
            "name": "Stationary Bike",
            "video_embed": "https://www.youtube.com/embed/rEqRmKAQ5xM",
            "category": "Low-Impact Cardio",
            "benefit": "Builds cardiovascular fitness while being kind to the joints.",
            "target": "Quads, glutes, calves, heart",
            "equipment": "Stationary bike",
            "steps": [
                "Adjust the seat so your knee stays slightly bent at the bottom.",
                "Start pedaling at a light resistance and smooth cadence.",
                "Keep your core engaged and avoid hunching over the handlebars.",
                "Cool down by lowering the resistance gradually.",
            ],
            "form_tip": "A smooth pedal stroke is more important than using high resistance early on.",
            "easier_option": "Lower the resistance and shorten the workout time.",
            "tips": {
                "beginner": "15 minutes at an easy pace.",
                "intermediate": "30 minutes of moderate effort.",
                "advanced": "45 minutes with interval blocks.",
            },
        },
        {
            "name": "Bodyweight Squat",
            "video_embed": "https://www.youtube.com/embed/P-yaD24bUE8",
            "category": "Strength",
            "benefit": "Builds foundational leg strength and movement confidence.",
            "target": "Quads, glutes, core",
            "equipment": "None",
            "steps": [
                "Stand with feet about shoulder-width apart.",
                "Brace your core and push your hips back as you bend your knees.",
                "Lower only as far as you can while keeping your chest up.",
                "Press through your feet to stand back up.",
            ],
            "form_tip": "Use a box or chair as a depth target if that helps you feel stable.",
            "easier_option": "Chair squat with support from your hands if needed.",
            "tips": {
                "beginner": "3 sets of 8 reps using a chair for support.",
                "intermediate": "4 sets of 10 reps with full bodyweight.",
                "advanced": "4 sets of 12 reps with light dumbbells.",
            },
        },
        {
            "name": "Wall Push-Up",
            "video_embed": "https://www.youtube.com/embed/ZUuYbRgcHmg",
            "category": "Strength",
            "benefit": "Develops pressing strength with less bodyweight load.",
            "target": "Chest, shoulders, triceps",
            "equipment": "Wall",
            "steps": [
                "Stand facing a wall with hands placed slightly wider than shoulders.",
                "Step your feet back until your body is at a gentle angle.",
                "Lower your chest toward the wall by bending your elbows.",
                "Press yourself back to the starting position.",
            ],
            "form_tip": "Keep your body in a straight line rather than bending at the hips.",
            "easier_option": "Stand closer to the wall.",
            "tips": {
                "beginner": "3 sets of 8 reps against the wall.",
                "intermediate": "3 sets of 10 reps on a bench incline.",
                "advanced": "3 sets of 10 standard push-ups.",
            },
        },
        {
            "name": "Hip Mobility Drills",
            "video_embed": "https://www.youtube.com/embed/WUKHM6-ekJM",
            "category": "Mobility",
            "benefit": "Helps hips move more freely and makes squats and walking feel easier.",
            "target": "Hips, glutes, lower back",
            "equipment": "Mat",
            "steps": [
                "Begin with gentle hip circles or seated hip rotations.",
                "Move slowly through a pain-free range of motion.",
                "Pause briefly in tight positions while breathing steadily.",
                "Repeat both sides evenly.",
            ],
            "form_tip": "Keep the motion gentle; mobility work should feel controlled, not forced.",
            "easier_option": "Perform the drills seated in a chair.",
            "tips": {
                "beginner": "5 minutes of simple hip circles and stretches.",
                "intermediate": "10 minutes of a flowing hip routine.",
                "advanced": "15 minutes with deeper mobility holds.",
            },
        },
        {
            "name": "Stretch & Breathe",
            "video_embed": "https://www.youtube.com/embed/n0sCHcQK4_0",
            "category": "Recovery",
            "benefit": "Reduces tension and helps your body recover between sessions.",
            "target": "Full body",
            "equipment": "Mat or quiet floor space",
            "steps": [
                "Choose a few easy stretches for hips, chest, and calves.",
                "Move into each stretch slowly and hold without pain.",
                "Take slow deep breaths while you hold the position.",
                "Finish with a couple of minutes of relaxed breathing.",
            ],
            "form_tip": "Long slow exhales help your muscles relax into the stretch.",
            "easier_option": "Shorter holds with fewer positions.",
            "tips": {
                "beginner": "10 minutes of gentle nightly stretching.",
                "intermediate": "15 minutes using a guided stretch routine.",
                "advanced": "20 minutes of mobility plus breathwork.",
            },
        },
    ],
    "obese": [
        {
            "name": "Walking",
            "video_embed": "https://www.youtube.com/embed/wQrV75N2BrI",
            "category": "Walking / Cycling",
            "benefit": "Builds a sustainable daily movement habit and improves stamina.",
            "target": "Heart health, calves, glutes",
            "equipment": "Walking shoes",
            "steps": [
                "Start at a comfortable pace you can repeat often.",
                "Keep your posture upright and your steps relaxed.",
                "Use natural arm swing to support your rhythm.",
                "Finish with a slower minute or two before stopping.",
            ],
            "form_tip": "Consistency matters more than speed at this stage.",
            "easier_option": "Break the walk into two or three shorter sessions.",
            "tips": {
                "beginner": "10 minutes, 5 days each week.",
                "intermediate": "20 to 30 minutes daily.",
                "advanced": "45 minutes at a brisk pace.",
            },
        },
        {
            "name": "Recumbent Bike",
            "video_embed": "https://www.youtube.com/embed/XugMoMDxyhM",
            "category": "Walking / Cycling",
            "benefit": "Adds low-impact cardio with back support and joint comfort.",
            "target": "Quads, calves, heart",
            "equipment": "Recumbent bike",
            "steps": [
                "Adjust the seat so your leg stays slightly bent at full extension.",
                "Sit tall against the backrest and begin pedaling smoothly.",
                "Use a comfortable resistance that you can maintain.",
                "Reduce resistance near the end to cool down.",
            ],
            "form_tip": "Smooth steady movement is more valuable than high resistance.",
            "easier_option": "Shorter sessions at lighter resistance.",
            "tips": {
                "beginner": "10 minutes at light resistance.",
                "intermediate": "25 minutes at a moderate pace.",
                "advanced": "40 minutes including short intervals.",
            },
        },
        {
            "name": "Water Walking",
            "video_embed": "https://www.youtube.com/embed/ZgxniVfKT4I",
            "category": "Water-Based Cardio",
            "benefit": "Uses water support to reduce impact while building endurance.",
            "target": "Full body, especially legs and core",
            "equipment": "Pool access",
            "steps": [
                "Enter shallow water where you feel stable and safe.",
                "Walk forward with controlled steps and upright posture.",
                "Use your arms naturally to balance and increase effort.",
                "Continue at a steady pace before slowing down to finish.",
            ],
            "form_tip": "Stay in a water depth that feels supportive rather than unstable.",
            "easier_option": "Shorter pool sessions with more rest.",
            "tips": {
                "beginner": "15 minutes of shallow-water walking.",
                "intermediate": "25 minutes with more arm movement.",
                "advanced": "40 minutes including light water jogging.",
            },
        },
        {
            "name": "Swimming",
            "video_embed": "https://www.youtube.com/embed/Eggwe7Z0XVA",
            "category": "Water-Based Cardio",
            "benefit": "Builds full-body conditioning while keeping joint stress low.",
            "target": "Shoulders, back, core, lungs",
            "equipment": "Pool",
            "steps": [
                "Start with easy laps or short lengths using a comfortable stroke.",
                "Focus on smooth breathing and relaxed body position in the water.",
                "Take breaks between lengths as needed.",
                "Cool down with a slower final lap or easy pool movement.",
            ],
            "form_tip": "Keep the effort gentle enough that you can maintain good breathing rhythm.",
            "easier_option": "Kickboard work or water walking between lengths.",
            "tips": {
                "beginner": "10 minutes at an easy pace.",
                "intermediate": "20 minutes mixing simple strokes.",
                "advanced": "30 or more minutes with interval laps.",
            },
        },
        {
            "name": "Seated Stretching",
            "video_embed": "https://www.youtube.com/embed/Wpj8BG73SNw",
            "category": "Mobility",
            "benefit": "Improves comfort and mobility with a very accessible setup.",
            "target": "Neck, shoulders, spine, hips",
            "equipment": "Chair",
            "steps": [
                "Sit tall near the front of a sturdy chair.",
                "Move through gentle stretches for the neck, shoulders, and legs.",
                "Hold each stretch with easy breathing and relaxed shoulders.",
                "Return to neutral posture slowly between stretches.",
            ],
            "form_tip": "Sit tall rather than collapsing into the chair while stretching.",
            "easier_option": "Use fewer stretches and shorter holds.",
            "tips": {
                "beginner": "10 minutes of chair-based stretching.",
                "intermediate": "15 minutes combining seated and standing options.",
                "advanced": "20 minutes of a fuller mobility routine.",
            },
        },
        {
            "name": "Diaphragmatic Breathing",
            "video_embed": "https://www.youtube.com/embed/9jpchJcKivk",
            "category": "Recovery",
            "benefit": "Improves calmness, recovery, and breathing awareness.",
            "target": "Diaphragm, core, nervous system",
            "equipment": "Quiet space",
            "steps": [
                "Sit or lie in a comfortable position with one hand on your stomach.",
                "Breathe in through your nose and feel your belly rise first.",
                "Exhale slowly and fully without shrugging your shoulders.",
                "Repeat for several relaxed breaths.",
            ],
            "form_tip": "Keep the inhale gentle; the goal is depth and control, not speed.",
            "easier_option": "Start with just two or three minutes.",
            "tips": {
                "beginner": "5 minutes of slow belly breathing.",
                "intermediate": "10 minutes using box breathing or guided cues.",
                "advanced": "15 minutes of guided recovery breathing.",
            },
        },
    ],
}


def get_exercise_plan(bmi_value: float, exercise_level: Optional[str]) -> dict:
    """Build a recommendation plan for the Exercise page."""
    category = _bmi_category(float(bmi_value))
    profile = _BMI_PROFILES[category]
    level_key = _normalize_level(exercise_level)

    exercises = []
    for item in _EXERCISES[category]:
        exercises.append(
            {
                "category": item["category"],
                "name": item["name"],
                "benefit": item["benefit"],
                "target": item["target"],
                "equipment": item["equipment"],
                "steps": item["steps"],
                "form_tip": item["form_tip"],
                "easier_option": item["easier_option"],
                "tip": item["tips"][level_key],
                "video": item.get("video"),
                "video_embed": item.get("video_embed"),
            }
        )

    return {
        "label": profile["label"],
        "focus": profile["focus"],
        "message": profile["message"],
        "categories": profile["categories"],
        "exercises": exercises,
    }
