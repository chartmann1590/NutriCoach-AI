#!/usr/bin/env python3
"""
Interactive admin user and profile creator for NutriCoach.

Usage (local):
  python create_admin_interactive.py

Usage (Docker):
  docker compose exec app python create_admin_interactive.py
"""

import os
import sys
import getpass
from typing import Optional

from app import create_app
from extensions import db
from models import User, Profile, Settings


def prompt(text: str, default: Optional[str] = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{text}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        print("Please enter a value.")


def prompt_int(text: str, default: Optional[int] = None, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    while True:
        raw = prompt(text, str(default) if default is not None else None)
        try:
            val = int(raw)
            if min_val is not None and val < min_val:
                print(f"Value must be >= {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"Value must be <= {max_val}")
                continue
            return val
        except ValueError:
            print("Please enter a valid integer.")


def prompt_float(text: str, default: Optional[float] = None, min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
    while True:
        raw = prompt(text, f"{default}" if default is not None else None)
        try:
            val = float(raw)
            if min_val is not None and val < min_val:
                print(f"Value must be >= {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"Value must be <= {max_val}")
                continue
            return val
        except ValueError:
            print("Please enter a valid number.")


def prompt_choice(text: str, choices: list[str], default: Optional[str] = None) -> str:
    choices_display = "/".join(choices)
    default = default if default in choices else None
    while True:
        raw = prompt(f"{text} ({choices_display})", default)
        if raw in choices:
            return raw
        print(f"Please choose one of: {choices_display}")


def prompt_password() -> str:
    while True:
        pw1 = getpass.getpass("Password (min 6 chars): ")
        if len(pw1) < 6:
            print("Password must be at least 6 characters.")
            continue
        pw2 = getpass.getpass("Confirm password: ")
        if pw1 != pw2:
            print("Passwords do not match. Try again.")
            continue
        return pw1


def main() -> int:
    print("\nNutriCoach Admin & Profile Setup")
    print("=" * 32)

    app = create_app()
    with app.app_context():
        # Ensure tables exist
        try:
            db.create_all()
        except Exception as e:
            print(f"Warning: could not ensure tables exist: {e}")

        # Username
        username = prompt("Admin username", "admin")
        user: Optional[User] = User.query.filter_by(username=username).first()

        if user:
            print(f"User '{username}' already exists.")
            elevate = prompt_choice("Make this user an admin?", ["y", "n"], "y")
            if elevate == "y":
                user.is_admin = True
            reset = prompt_choice("Reset this user's password?", ["y", "n"], "n")
            if reset == "y":
                password = prompt_password()
                user.set_password(password)
        else:
            print("Creating new admin user...")
            password = prompt_password()
            user = User(username=username, is_admin=True, is_active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # get user.id

        # Profile
        print("\nProfile details (press Enter to accept defaults)")
        name = prompt("Full name", "Admin User")
        age = prompt_int("Age", 30, 13, 120)
        sex = prompt_choice("Sex", ["male", "female", "other"], "male")
        height_cm = prompt_float("Height (cm)", 175.0, 100.0, 250.0)
        weight_kg = prompt_float("Current weight (kg)", 75.0, 30.0, 300.0)
        activity_level = prompt_choice("Activity level", ["sedentary", "light", "moderate", "active", "very_active"], "moderate")
        goal_type = prompt_choice("Goal type", ["lose", "maintain", "gain"], "maintain")

        target_weight_kg: Optional[float] = None
        timeframe_weeks: Optional[int] = None
        if goal_type in ("lose", "gain"):
            target_weight_kg = prompt_float("Target weight (kg)", weight_kg)
            timeframe_weeks = prompt_int("Timeframe (weeks)", 12, 1, 520)

        profile: Optional[Profile] = Profile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = Profile(
                user_id=user.id,
                name=name,
                age=age,
                sex=sex,
                height_cm=height_cm,
                weight_kg=weight_kg,
                activity_level=activity_level,
                goal_type=goal_type,
                target_weight_kg=target_weight_kg,
                timeframe_weeks=timeframe_weeks,
            )
            db.session.add(profile)
        else:
            profile.name = name
            profile.age = age
            profile.sex = sex
            profile.height_cm = height_cm
            profile.weight_kg = weight_kg
            profile.activity_level = activity_level
            profile.goal_type = goal_type
            profile.target_weight_kg = target_weight_kg
            profile.timeframe_weeks = timeframe_weeks

        # Settings (per-user)
        ollama_default = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        settings: Optional[Settings] = Settings.query.filter_by(user_id=user.id).first()
        if not settings:
            settings = Settings(
                user_id=user.id,
                ollama_url=ollama_default,
                safety_mode=True,
            )
            db.session.add(settings)
        else:
            if not settings.ollama_url:
                settings.ollama_url = ollama_default

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"\nERROR: Failed to save admin user: {e}")
            return 1

        print("\nSuccess! Admin user ready.")
        print("- Username:", user.username)
        print("- is_admin:", user.is_admin)
        print("- Profile:", profile.name, f"({profile.age}y, {profile.sex}, {profile.height_cm}cm, {profile.weight_kg}kg)")

        print("\nNext steps:")
        print("- Login at /auth/login")
        print("- Admin dashboard: /admin/dashboard")
        print("\nDocker (default): http://localhost:5001")
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
        raise SystemExit(130)


