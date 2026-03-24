"""
Swimming Calorie Tracker
A comprehensive application that tracks calories burned based on swimming strokes and duration.

Formula: Calories = (Stroke MET value × User Weight in kg × Duration in minutes) / 60
"""

import json
import os
from datetime import datetime

# MET (Metabolic Equivalent) values for each stroke and intensity level
# Source: Compendium of Physical Activities
STROKE_METS = {
    "freestyle": {
        "easy": 5.8,
        "moderate": 8.3,
        "intense": 10.0,
    },
    "breaststroke": {
        "easy": 5.3,
        "moderate": 7.0,
        "intense": 9.8,
    },
    "backstroke": {
        "easy": 4.8,
        "moderate": 6.0,
        "intense": 8.0,
    },
    "butterfly": {
        "easy": 8.0,
        "moderate": 11.0,
        "intense": 13.8,
    },
}

# Average speed in meters per minute for distance estimation
STROKE_SPEEDS = {
    "freestyle": {"easy": 30, "moderate": 45, "intense": 60},
    "breaststroke": {"easy": 20, "moderate": 30, "intense": 45},
    "backstroke": {"easy": 25, "moderate": 35, "intense": 50},
    "butterfly": {"easy": 20, "moderate": 30, "intense": 42},
}

DATA_FILE = "data/swimming_sessions.json"


def calculate_calories(stroke: str, intensity: str, duration_minutes: float, weight_kg: float) -> float:
    """
    Calculate calories burned during a swim session.

    Args:
        stroke: Swimming stroke name (freestyle, breaststroke, backstroke, butterfly)
        intensity: Intensity level (easy, moderate, intense)
        duration_minutes: Duration of the swim in minutes
        weight_kg: User weight in kilograms

    Returns:
        Calories burned as a float
    """
    met = STROKE_METS[stroke][intensity]
    calories = (met * weight_kg * duration_minutes) / 60
    return round(calories, 2)


def estimate_distance(stroke: str, intensity: str, duration_minutes: float) -> float:
    """
    Estimate distance swum in meters.

    Args:
        stroke: Swimming stroke name
        intensity: Intensity level
        duration_minutes: Duration in minutes

    Returns:
        Estimated distance in meters
    """
    speed = STROKE_SPEEDS[stroke][intensity]
    return round(speed * duration_minutes, 1)


def create_session(
    stroke: str,
    intensity: str,
    duration_minutes: float,
    weight_kg: float,
    notes: str = "",
) -> dict:
    """
    Create a new swimming session record.

    Args:
        stroke: Swimming stroke name
        intensity: Intensity level
        duration_minutes: Duration in minutes
        weight_kg: User weight in kilograms
        notes: Optional notes about the session

    Returns:
        A dictionary representing the swim session
    """
    calories = calculate_calories(stroke, intensity, duration_minutes, weight_kg)
    distance = estimate_distance(stroke, intensity, duration_minutes)
    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "stroke": stroke,
        "intensity": intensity,
        "duration_minutes": duration_minutes,
        "weight_kg": weight_kg,
        "calories_burned": calories,
        "distance_meters": distance,
        "notes": notes,
    }


def load_sessions(filepath: str = DATA_FILE) -> list:
    """
    Load swimming sessions from a JSON file.

    Args:
        filepath: Path to the JSON data file

    Returns:
        List of session dictionaries
    """
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)


def save_sessions(sessions: list, filepath: str = DATA_FILE) -> None:
    """
    Save swimming sessions to a JSON file.

    Args:
        sessions: List of session dictionaries
        filepath: Path to the JSON data file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(sessions, f, indent=2)


def add_session(session: dict, filepath: str = DATA_FILE) -> list:
    """
    Add a new session to the stored sessions.

    Args:
        session: Session dictionary to add
        filepath: Path to the JSON data file

    Returns:
        Updated list of sessions
    """
    sessions = load_sessions(filepath)
    sessions.append(session)
    save_sessions(sessions, filepath)
    return sessions


def delete_session(session_id: str, filepath: str = DATA_FILE) -> list:
    """
    Delete a session by its ID.

    Args:
        session_id: The unique ID of the session to delete
        filepath: Path to the JSON data file

    Returns:
        Updated list of sessions
    """
    sessions = load_sessions(filepath)
    sessions = [s for s in sessions if s["id"] != session_id]
    save_sessions(sessions, filepath)
    return sessions


def get_statistics(sessions: list) -> dict:
    """
    Calculate aggregate statistics across all sessions.

    Args:
        sessions: List of session dictionaries

    Returns:
        Dictionary of statistics
    """
    if not sessions:
        return {
            "total_sessions": 0,
            "total_calories": 0.0,
            "total_duration_minutes": 0.0,
            "total_distance_meters": 0.0,
            "avg_calories_per_session": 0.0,
            "avg_duration_per_session": 0.0,
            "stroke_breakdown": {},
        }

    total_calories = sum(s["calories_burned"] for s in sessions)
    total_duration = sum(s["duration_minutes"] for s in sessions)
    total_distance = sum(s["distance_meters"] for s in sessions)

    stroke_breakdown = {}
    for s in sessions:
        stroke = s["stroke"]
        if stroke not in stroke_breakdown:
            stroke_breakdown[stroke] = {"sessions": 0, "calories": 0.0, "duration": 0.0}
        stroke_breakdown[stroke]["sessions"] += 1
        stroke_breakdown[stroke]["calories"] += s["calories_burned"]
        stroke_breakdown[stroke]["duration"] += s["duration_minutes"]

    return {
        "total_sessions": len(sessions),
        "total_calories": round(total_calories, 2),
        "total_duration_minutes": round(total_duration, 2),
        "total_distance_meters": round(total_distance, 1),
        "avg_calories_per_session": round(total_calories / len(sessions), 2),
        "avg_duration_per_session": round(total_duration / len(sessions), 2),
        "stroke_breakdown": stroke_breakdown,
    }


def generate_report(sessions: list) -> str:
    """
    Generate a text report of swimming activity.

    Args:
        sessions: List of session dictionaries

    Returns:
        Formatted report string
    """
    stats = get_statistics(sessions)
    lines = [
        "=" * 50,
        "       SWIMMING ACTIVITY REPORT",
        "=" * 50,
        f"Total Sessions:       {stats['total_sessions']}",
        f"Total Calories:       {stats['total_calories']} kcal",
        f"Total Duration:       {stats['total_duration_minutes']} min",
        f"Total Distance:       {stats['total_distance_meters']} m",
        f"Avg Calories/Session: {stats['avg_calories_per_session']} kcal",
        f"Avg Duration/Session: {stats['avg_duration_per_session']} min",
        "",
        "--- Stroke Breakdown ---",
    ]
    for stroke, data in stats["stroke_breakdown"].items():
        lines.append(
            f"  {stroke.capitalize():<14}: {data['sessions']} sessions, "
            f"{round(data['calories'], 2)} kcal, {round(data['duration'], 1)} min"
        )
    lines.append("=" * 50)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------

def _prompt_stroke() -> str:
    strokes = list(STROKE_METS.keys())
    print("\nAvailable strokes:")
    for i, s in enumerate(strokes, 1):
        print(f"  {i}. {s.capitalize()}")
    while True:
        choice = input("Select stroke (1-4): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(strokes):
            return strokes[int(choice) - 1]
        print("Invalid choice, please try again.")


def _prompt_intensity() -> str:
    levels = ["easy", "moderate", "intense"]
    print("\nIntensity levels:")
    for i, lvl in enumerate(levels, 1):
        print(f"  {i}. {lvl.capitalize()}")
    while True:
        choice = input("Select intensity (1-3): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(levels):
            return levels[int(choice) - 1]
        print("Invalid choice, please try again.")


def _prompt_float(prompt: str, min_val: float = 0.01) -> float:
    while True:
        try:
            val = float(input(prompt).strip())
            if val >= min_val:
                return val
            print(f"Value must be at least {min_val}.")
        except ValueError:
            print("Please enter a valid number.")


def cli_log_session() -> None:
    """Interactively log a new swim session via the command line."""
    print("\n--- Log a New Swim Session ---")
    stroke = _prompt_stroke()
    intensity = _prompt_intensity()
    duration = _prompt_float("Duration (minutes): ")
    weight = _prompt_float("Your weight (kg): ")
    notes = input("Notes (optional, press Enter to skip): ").strip()

    session = create_session(stroke, intensity, duration, weight, notes)
    add_session(session)

    print(f"\n✅ Session logged!")
    print(f"   Stroke:   {session['stroke'].capitalize()}")
    print(f"   Intensity: {session['intensity'].capitalize()}")
    print(f"   Duration: {session['duration_minutes']} min")
    print(f"   Distance: {session['distance_meters']} m")
    print(f"   Calories: {session['calories_burned']} kcal")


def cli_view_sessions() -> None:
    """Display all logged sessions."""
    sessions = load_sessions()
    if not sessions:
        print("\nNo sessions logged yet.")
        return
    print(f"\n--- Session Log ({len(sessions)} sessions) ---")
    for i, s in enumerate(sessions, 1):
        print(
            f"{i:>3}. [{s['date']} {s['time']}] "
            f"{s['stroke'].capitalize()} ({s['intensity']}) — "
            f"{s['duration_minutes']} min, {s['calories_burned']} kcal, "
            f"{s['distance_meters']} m"
        )
        if s.get("notes"):
            print(f"       Notes: {s['notes']}")


def cli_delete_session() -> None:
    """Delete a session by index."""
    sessions = load_sessions()
    if not sessions:
        print("\nNo sessions to delete.")
        return
    cli_view_sessions()
    while True:
        choice = input("\nEnter session number to delete (or 0 to cancel): ").strip()
        if choice.isdigit():
            idx = int(choice)
            if idx == 0:
                return
            if 1 <= idx <= len(sessions):
                session_id = sessions[idx - 1]["id"]
                delete_session(session_id)
                print("✅ Session deleted.")
                return
        print("Invalid number.")


def cli_view_statistics() -> None:
    """Display aggregate statistics."""
    sessions = load_sessions()
    print("\n" + generate_report(sessions))


def main() -> None:
    """Main command-line interface loop."""
    print("\n🏊 Swimming Calorie Tracker")
    print("=" * 30)

    while True:
        print("\nMain Menu:")
        print("  1. Log a new swim session")
        print("  2. View all sessions")
        print("  3. Delete a session")
        print("  4. View statistics / report")
        print("  5. Exit")

        choice = input("\nChoose an option (1-5): ").strip()
        if choice == "1":
            cli_log_session()
        elif choice == "2":
            cli_view_sessions()
        elif choice == "3":
            cli_delete_session()
        elif choice == "4":
            cli_view_statistics()
        elif choice == "5":
            print("\nGoodbye! Keep swimming! 🏊")
            break
        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    main()
