# 🏊 Swimming Calorie Tracker

A comprehensive Python application that tracks calories burned based on swimming strokes and duration.

## Features

- **4 swimming strokes**: Freestyle, Breaststroke, Backstroke, Butterfly
- **3 intensity levels** per stroke: Easy, Moderate, Intense
- **MET-based calorie calculation**: `Calories = (MET × Weight in kg × Duration in min) / 60`
- **Distance estimation** based on stroke speed
- **Persistent session log** stored as JSON
- **Statistics & reports** — totals, averages, and stroke breakdown
- **Streamlit web app** — interactive UI with charts
- **Command-line interface** — run without a browser

## How to Run

### 1. Install the requirements

```
pip install -r requirements.txt
```

### 2. Streamlit Web App

```
streamlit run streamlit_app.py
```

### 3. Command-Line Interface

```
python swimming_tracker.py
```

## MET Values Used

| Stroke       | Easy | Moderate | Intense |
|-------------|------|----------|---------|
| Freestyle    | 5.8  | 8.3      | 10.0    |
| Breaststroke | 5.3  | 7.0      | 9.8     |
| Backstroke   | 4.8  | 6.0      | 8.0     |
| Butterfly    | 8.0  | 11.0     | 13.8    |

## Project Structure

```
Swimming_Strokes/
├── streamlit_app.py       # Streamlit web UI
├── swimming_tracker.py    # Core logic + CLI
├── requirements.txt       # Python dependencies
└── data/
    └── swimming_sessions.json  # Persistent session storage
```

## Example Usage (CLI)

```
🏊 Swimming Calorie Tracker
==============================

Main Menu:
  1. Log a new swim session
  2. View all sessions
  3. Delete a session
  4. View statistics / report
  5. Exit
```

