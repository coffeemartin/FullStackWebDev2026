from app import db
from app.models import LLMRecommendation, Exercise
import json


def calculate_bmi_result(height_cm, weight_kg):
    height = float(height_cm)
    weight = float(weight_kg)
    if height <= 0 or weight <= 0:
        raise ValueError("Please enter a valid height and weight.")

    height_m = height / 100
    bmi = round(weight / (height_m ** 2), 1)

    if bmi < 18.5:
        return bmi, "Underweight", "Start building strength and nourish your body!"
    if bmi < 25:
        return bmi, "Healthy weight", "Great shape! Keep maintaining your healthy lifestyle!"
    if bmi < 30:
        return bmi, "Overweight", "You are doing well. Let us improve fitness step by step!"
    return bmi, "Obese", "Start your fitness journey today. Small steps make big changes!"


def get_bmi_fitness_points(category):
    points_by_category = {
        "Underweight": [
            "Prioritise balanced meals with enough protein and healthy carbohydrates.",
            "Use strength training to build muscle gradually.",
            "Keep cardio light to moderate while you focus on healthy weight gain.",
            "Track energy levels so workouts support recovery, not exhaustion.",
            "Speak with a health professional if weight gain is difficult."
        ],
        "Healthy weight": [
            "Maintain your current habits with consistent weekly movement.",
            "Mix strength, cardio, mobility, and recovery for balance.",
            "Keep protein, vegetables, hydration, and sleep in your routine.",
            "Set performance goals such as more reps, better pace, or flexibility.",
            "Use your BMI as one guide, not the only measure of progress."
        ],
        "Overweight": [
            "Start with realistic sessions such as walking, cycling, or full-body circuits.",
            "Add strength training to support metabolism and protect joints.",
            "Choose small nutrition changes you can repeat every week.",
            "Increase workout time slowly instead of jumping into intense plans.",
            "Celebrate consistency before focusing only on the scale."
        ],
        "Obese": [
            "Begin with low-impact exercise to protect knees, hips, and back.",
            "Aim for short, repeatable movement sessions throughout the week.",
            "Pair activity with simple meal planning and regular hydration.",
            "Use strength exercises at a comfortable level to build confidence.",
            "Consider professional guidance for a safe long-term plan."
        ]
    }
    return points_by_category.get(category, [
        "Add height and weight to unlock BMI-based fitness guidance.",
        "Begin with simple movement you can repeat consistently.",
        "Balance exercise with sleep, hydration, and nutrition.",
        "Avoid comparing your progress with someone else's journey.",
        "Small improvements each week can become lasting habits."
    ])



def save_ai_all_controller(recommendation_id, user_id, training_plan_json, mark_saved=False):
    """
    Franco notes: this is a refactored version of the save_ai_all function from routes.py, modified to be suitable for unit testing. It
    removed request / flash / redirect / url_for / current_user dependencies, and instead takes in the necessary parameters directly. 
    

    This routes does two things : 
    
    1. Saves edited AI training plan 
    2. Inserts new exercises into Exercise dimension table. (If AI returns new excercises that are not in the database, 
    I need to add them to the Exercise dimension table.

    """

    if recommendation_id is None or not training_plan_json:
        return {
            "success": False,
            "message": "Could not save that plan."
        }

    recommendation = LLMRecommendation.query.filter_by(
        id=recommendation_id,
        user_id=user_id,
    ).first()

    if recommendation is None:
        return {
            "success": False,
            "message": "Could not find that AI plan."
        }

    try:
        training_plan = json.loads(training_plan_json)
    except Exception:
        return {
            "success": False,
            "message": "Invalid plan data."
        }

    recommendation.set_training_plan(training_plan)

    warning_message = None

    try:
        for day in training_plan:
            for exercise in day.get("exercises", []):
                exercise_name = exercise.get("name", "").strip()

                if exercise_name:
                    existing_exercise = Exercise.query.filter(
                        db.func.lower(Exercise.name) == exercise_name.lower()
                    ).first()

                    if existing_exercise is None:
                        new_exercise = Exercise(
                            name=exercise_name,
                            category=None,
                            muscle_group=None,
                            equipment=None,
                        )
                        db.session.add(new_exercise)

    except Exception as e:
        warning_message = f"Warning: Could not add some exercises: {str(e)}"

    if mark_saved:
        recommendation.user_saved = True

    db.session.commit()

    return {
        "success": True,
        "message": "All edits saved.",
        "mark_saved": mark_saved,
        "warning": warning_message,
        "recommendation_id": recommendation.id,
    }