from app import db
from app.models import LLMRecommendation, Exercise
import json
from unittest import TestCase


# Franco Notes: Refactor the code in routes.py to controllers.py, so that the logic is separated from the route handling.
# logic originally in the AI routes
def normalise_ai_generation_options(history_days, temperature, max_history_days=90):
    try:
        days = int(history_days)
    except (TypeError, ValueError):
        days = 30

    if days < 1:
        days = 1
    if days > max_history_days:
        days = max_history_days

    try:
        temperature_value = float(temperature)
    except (TypeError, ValueError):
        temperature_value = 0.0

    if temperature_value < 0:
        temperature_value = 0.0
    if temperature_value > 1:
        temperature_value = 1.0

    return days, temperature_value

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



