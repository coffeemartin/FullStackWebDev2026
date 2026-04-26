from datetime import datetime, date
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100)) 
    age: so.Mapped[Optional[int]]
    gender: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    height_cm: so.Mapped[Optional[float]]
    weight_kg: so.Mapped[Optional[float]]

    goal: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
    activity_level: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    injury_notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    exercise_logs: so.Mapped[list["ExerciseLog"]] = so.relationship(back_populates="user")
    nutrition_logs: so.Mapped[list["NutritionLog"]] = so.relationship(back_populates="user")
    recommendations: so.Mapped[list["LLMRecommendation"]] = so.relationship(back_populates="user")

    def __repr__(self):
        return f"<{self.name}>"

class Exercise(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True, index=True)
    category: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    muscle_group: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    equipment: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))

    logs: so.Mapped[list["ExerciseLog"]] = so.relationship(back_populates="exercise")
    
    def __repr__(self):
        return f"<{self.name}>"

class ExerciseLog(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    exercise_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("exercise.id"), index=True)

    log_date: so.Mapped[date] = so.mapped_column(default=date.today)
    sets: so.Mapped[Optional[int]]
    reps: so.Mapped[Optional[int]]
    weight_kg: so.Mapped[Optional[float]]
    duration_minutes: so.Mapped[Optional[int]]
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    user: so.Mapped["User"] = so.relationship(back_populates="exercise_logs")
    exercise: so.Mapped["Exercise"] = so.relationship(back_populates="logs")

class Food(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True, index=True)

    calories_per_100g: so.Mapped[Optional[float]]
    protein_per_100g: so.Mapped[Optional[float]]
    carbs_per_100g: so.Mapped[Optional[float]]
    fat_per_100g: so.Mapped[Optional[float]]

    logs: so.Mapped[list["NutritionLog"]] = so.relationship(back_populates="food")

class NutritionLog(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    food_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("food.id"), index=True)

    log_date: so.Mapped[date] = so.mapped_column(default=date.today)
    meal_type: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))
    quantity_g: so.Mapped[Optional[float]]
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    user: so.Mapped["User"] = so.relationship(back_populates="nutrition_logs")
    food: so.Mapped["Food"] = so.relationship(back_populates="logs")

class LLMRecommendation(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    input_summary: so.Mapped[str] = so.mapped_column(sa.Text)
    llm_comments: so.Mapped[str] = so.mapped_column(sa.Text)

    training_plan: so.Mapped[str] = so.mapped_column(sa.Text)
    nutrition_plan: so.Mapped[str] = so.mapped_column(sa.Text)

    user: so.Mapped["User"] = so.relationship(back_populates="recommendations")

class UserEmbedding(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    source_type: so.Mapped[str] = so.mapped_column(sa.String(50))
    source_id: so.Mapped[int]

    text_chunk: so.Mapped[str] = so.mapped_column(sa.Text)
    embedding_json: so.Mapped[str] = so.mapped_column(sa.Text)

    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)