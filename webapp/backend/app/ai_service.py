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


def generate_ai_plan(ai_input: dict) -> dict:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a fitness and nutrition assistant. "
                    "Use the user's profile, exercise logs, and nutrition logs. "
                    "Return practical, safe, beginner-friendly advice. "
                    "Do not provide medical diagnosis."
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
    # Normalize exercise names to single values (not "x or y")
    plan = normalize_training_plan(plan)
    return plan