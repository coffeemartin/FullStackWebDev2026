from datetime import datetime, date
import json
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Login/auth fields
    username: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True, index=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))


    name: so.Mapped[str] = so.mapped_column(sa.String(100)) 
    age: so.Mapped[Optional[int]] = so.mapped_column(nullable=True)
    gender: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    height_cm: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)
    weight_kg: so.Mapped[Optional[float]] = so.mapped_column(nullable=True)

    goal: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
    activity_level: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    injury_notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    # Audit fields
    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    last_login_at: so.Mapped[Optional[datetime]] 

    exercise_logs: so.Mapped[list["ExerciseLog"]] = so.relationship(back_populates="user")
    nutrition_logs: so.Mapped[list["NutritionLog"]] = so.relationship(back_populates="user")
    recommendations: so.Mapped[list["LLMRecommendation"]] = so.relationship(back_populates="user")
    login_events: so.Mapped[list["LoginEvent"]] = so.relationship(back_populates="user")
    embeddings: so.Mapped[list["UserEmbedding"]] = so.relationship(back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
   
class LoginEvent(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    login_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    ip_address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(45))
    user_agent: so.Mapped[Optional[str]] = so.mapped_column(sa.String(300))
    success: so.Mapped[bool] = so.mapped_column(default=True)

    user: so.Mapped["User"] = so.relationship(back_populates="login_events")

class Exercise(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True, index=True)
    category: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    muscle_group: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    equipment: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))

    logs: so.Mapped[list["ExerciseLog"]] = so.relationship(back_populates="exercise")
    
    def __repr__(self):
        return f"<Exercise {self.name}>"

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

    training_plan_json: so.Mapped[str] = so.mapped_column(sa.Text)
    nutrition_plan_json: so.Mapped[str] = so.mapped_column(sa.Text)

    user: so.Mapped["User"] = so.relationship(back_populates="recommendations")

    # Helper methods 
    # Set is to convert dict to json string for stroage,
    # Get is to convert json string back to dict for use in the app.
    def set_training_plan(self, data: dict):
        self.training_plan_json = json.dumps(data)

    def get_training_plan(self):
        return json.loads(self.training_plan_json) if self.training_plan_json else None

    def set_nutrition_plan(self, data: dict):
        self.nutrition_plan_json = json.dumps(data)

    def get_nutrition_plan(self):
        return json.loads(self.nutrition_plan_json) if self.nutrition_plan_json else None
    

    
class UserEmbedding(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    user: so.Mapped["User"] = so.relationship(back_populates="embeddings")
    source_type: so.Mapped[str] = so.mapped_column(sa.String(50))
    source_id: so.Mapped[int]

    text_chunk: so.Mapped[str] = so.mapped_column(sa.Text)
    embedding_json: so.Mapped[str] = so.mapped_column(sa.Text)

    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    