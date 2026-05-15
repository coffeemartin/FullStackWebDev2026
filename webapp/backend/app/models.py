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
    sent_friendships: so.Mapped[list["Friendship"]] = so.relationship(
        foreign_keys="Friendship.requester_id",
        back_populates="requester",
        cascade="all, delete-orphan",
    )
    received_friendships: so.Mapped[list["Friendship"]] = so.relationship(
        foreign_keys="Friendship.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )

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


class Friendship(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    requester_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    receiver_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    status: so.Mapped[str] = so.mapped_column(sa.String(20), default="pending", server_default="pending", index=True)
    created_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    requester: so.Mapped["User"] = so.relationship(
        foreign_keys=[requester_id],
        back_populates="sent_friendships",
    )
    receiver: so.Mapped["User"] = so.relationship(
        foreign_keys=[receiver_id],
        back_populates="received_friendships",
    )

    __table_args__ = (
        sa.UniqueConstraint("requester_id", "receiver_id", name="uq_friendship_request_pair"),
        sa.CheckConstraint("requester_id != receiver_id", name="ck_friendship_not_self"),
    )

    def __repr__(self):
        return f"<Friendship {self.requester_id}->{self.receiver_id} {self.status}>"


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
    water_glasses: so.Mapped[Optional[int]]
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
    user_saved: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, server_default=sa.false())
    is_current: so.Mapped[Optional[bool]] = so.mapped_column(sa.Boolean, nullable=True, default=None)


# The frontend will handle the logic to set is_current=True for the selected plan and is_current=False for all other plans of the user when they mark a plan as current.
# The route handler will also ensure that when a new plan is generated and marked as current, all other plans for that user are automatically updated to is_current=False, so the user doesn't have to manually unmark the previous current plan.
# But below is database level validation, Not just frontend!!!! Not just Flask backend validation !!!!
# this is the safety net to ensure data integrity at the database level.
# Add a unique partial index to enforce that each user can only have one recommendation marked as current.
    __table_args__ = (
        sa.Index(
            "uq_llm_recommendation_one_current_per_user",
            "user_id",
            unique=True,
            sqlite_where=sa.text("is_current = 1"),
            postgresql_where=sa.text("is_current IS TRUE"),
        ),
    )

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
