import json
import re
from openai import OpenAI


client = OpenAI()


def normalize_exercise_name(exercise_name: str) -> str:
    """
    Normalize exercise names by removing alternatives.
    E.g., "Pushups or Bench Press" -> "Pushups"
    
    This ensures exercise names match the Exercise dimension table
    which requires singular, definitive values.
    """
    # Handle "X or Y" or "X / Y" patterns - take the first option
    if " or " in exercise_name:
        exercise_name = exercise_name.split(" or ")[0]
    elif " / " in exercise_name:
        exercise_name = exercise_name.split(" / ")[0]
    
    # Clean up extra whitespace
    return exercise_name.strip()


def normalize_training_plan(plan: dict) -> dict:
    """
    Normalize the training plan by ensuring all exercise names are singular.
    """
    for day in plan.get("weekly_training_plan", []):
        for exercise in day.get("exercises", []):
            if "name" in exercise:
                exercise["name"] = normalize_exercise_name(exercise["name"])
    return plan

# Franco Notes: use the OpenAI client to generate a training and nutrition plan based on the user's profile and recent logs. 
# The system prompt instructs the model to provide practical, safe, beginner-friendly advice and to format exercise
# I have also particularly emphasized the need to use generic exercise names for the exercise.name field, 
# and to move any modifiers into the exercise.notes field.
# Given clear examples in the propmt, the model should learn to output exercise names that are suitable for matching against an Exercise dimension table in the database,
def generate_ai_plan(ai_input: dict, temperature: float = 0.0) -> dict:
    # Bound model temperature to the supported UI range [0, 1].
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        temperature = 0.0

    if temperature < 0:
        temperature = 0.0
    if temperature > 1:
        temperature = 1.0

    response = client.responses.create(
        model="gpt-4.1-mini",
        temperature=temperature,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a fitness and nutrition assistant. "
                    "Use the user's profile, exercise logs, and nutrition logs. "
                    "Return practical, safe, beginner-friendly advice. "
                    "Do not provide medical diagnosis. "
                    "Use generic canonical exercise names only for exercise.name. "
                    "Do not include variations, locations, equipment setup, difficulty level, brackets, slashes, alternatives, or instructions in exercise.name. "
                    "Move all modifiers into exercise.notes. "
                    "For example: use name='Dumbbell Chest Press' and notes='Perform on the floor if no bench is available.' "
                    "For example: use name='Plank' and notes='Use knee plank or standard plank depending on ability.' "
                    "For example: use name='Push-up' and notes='Can be performed on knees, incline, or standard.' "
                    "Exercise names should be suitable for an Exercise dimension table."
                    "Add a matching emoji at the beginning of each nutrition goal suggestion for quick visual identification (e.g., 💧 for Hydration)."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(ai_input),
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "fitness_plan",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "summary_comment": {"type": "string"},
                        "training_focus": {"type": "string"},
                        "nutrition_focus": {"type": "string"},
                        "weekly_training_plan": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "day": {"type": "string"},
                                    "focus": {"type": "string"},
                                    "exercises": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "additionalProperties": False,
                                            "properties": {
                                                "name": {"type": "string"},
                                                "sets": {"type": "string"},
                                                "reps": {"type": "string"},
                                                "duration_minutes": {"type": "string"},
                                                "notes": {"type": "string"},
                                            },
                                            "required": [
                                                "name",
                                                "sets",
                                                "reps",
                                                "duration_minutes",
                                                "notes",
                                            ],
                                        },
                                    },
                                },
                                "required": ["day", "focus", "exercises"],
                            },
                        },
                        "nutrition_plan": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "goal": {"type": "string"},
                                    "suggestion": {"type": "string"},
                                },
                                "required": ["goal", "suggestion"],
                            },
                        },
                        "warnings": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "summary_comment",
                        "training_focus",
                        "nutrition_focus",
                        "weekly_training_plan",
                        "nutrition_plan",
                        "warnings",
                    ],
                },
            }
        },
    )

    plan = json.loads(response.output_text)
    # Franco Notes: Normalize exercise names to single values (not "x or y")
    plan = normalize_training_plan(plan)
    return plan