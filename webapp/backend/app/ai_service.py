import json
from openai import OpenAI


client = OpenAI()


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

    return json.loads(response.output_text)