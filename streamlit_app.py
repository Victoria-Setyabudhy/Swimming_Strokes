"""
Swimming Calorie Tracker — Streamlit Web Application
"""

import streamlit as st
import pandas as pd

from swimming_tracker import (
    STROKE_METS,
    add_session,
    calculate_calories,
    create_session,
    delete_session,
    estimate_distance,
    generate_report,
    get_statistics,
    load_sessions,
)

st.set_page_config(page_title="🏊 Swimming Calorie Tracker", page_icon="🏊", layout="wide")

st.title("🏊 Swimming Calorie Tracker")
st.write("Track calories burned based on your swimming strokes and duration.")

# Sidebar — log a new session
st.sidebar.header("Log a New Swim Session")

with st.sidebar.form("log_session_form"):
    stroke = st.selectbox(
        "Stroke",
        options=list(STROKE_METS.keys()),
        format_func=lambda x: x.capitalize(),
    )
    intensity = st.selectbox(
        "Intensity",
        options=["easy", "moderate", "intense"],
        format_func=lambda x: x.capitalize(),
    )
    duration = st.number_input("Duration (minutes)", min_value=1.0, max_value=300.0, value=30.0, step=1.0)
    weight = st.number_input("Your weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
    notes = st.text_input("Notes (optional)")
    submitted = st.form_submit_button("➕ Log Session")

if submitted:
    session = create_session(stroke, intensity, duration, weight, notes)
    add_session(session)
    st.sidebar.success(
        f"Session logged! {session['calories_burned']} kcal burned in {duration} min."
    )

# MET reference table
with st.sidebar.expander("📊 MET Reference Values"):
    met_rows = []
    for s, intensities in STROKE_METS.items():
        for lvl, met in intensities.items():
            met_rows.append({"Stroke": s.capitalize(), "Intensity": lvl.capitalize(), "MET": met})
    st.dataframe(pd.DataFrame(met_rows), hide_index=True, use_container_width=True)

# Main content
sessions = load_sessions()

tab1, tab2, tab3 = st.tabs(["📋 Session Log", "📈 Statistics", "🧮 Calorie Calculator"])

# ── Tab 1: Session Log ──────────────────────────────────────────────────────
with tab1:
    if not sessions:
        st.info("No sessions logged yet. Use the sidebar to log your first swim!")
    else:
        rows = []
        for s in sessions:
            rows.append({
                "ID": s["id"],
                "Date": s["date"],
                "Time": s["time"],
                "Stroke": s["stroke"].capitalize(),
                "Intensity": s["intensity"].capitalize(),
                "Duration (min)": s["duration_minutes"],
                "Distance (m)": s["distance_meters"],
                "Calories (kcal)": s["calories_burned"],
                "Weight (kg)": s["weight_kg"],
                "Notes": s.get("notes", ""),
            })
        df = pd.DataFrame(rows)

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sessions", len(sessions))
        col2.metric("Total Calories", f"{df['Calories (kcal)'].sum():.1f} kcal")
        col3.metric("Total Duration", f"{df['Duration (min)'].sum():.0f} min")
        col4.metric("Total Distance", f"{df['Distance (m)'].sum():.0f} m")

        st.dataframe(
            df.drop(columns=["ID"]),
            use_container_width=True,
            hide_index=True,
        )

        # Delete a session
        st.subheader("Delete a Session")
        session_labels = [
            f"{s['date']} {s['time']} — {s['stroke'].capitalize()} ({s['intensity']}) {s['duration_minutes']} min"
            for s in sessions
        ]
        selected_label = st.selectbox("Select session to delete", options=["— select —"] + session_labels)
        if st.button("🗑️ Delete Selected Session"):
            if selected_label != "— select —":
                idx = session_labels.index(selected_label)
                delete_session(sessions[idx]["id"])
                st.rerun()
            else:
                st.warning("Please select a session to delete.")

# ── Tab 2: Statistics ───────────────────────────────────────────────────────
with tab2:
    stats = get_statistics(sessions)
    if stats["total_sessions"] == 0:
        st.info("No sessions logged yet.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sessions", stats["total_sessions"])
        col2.metric("Total Calories", f"{stats['total_calories']} kcal")
        col3.metric("Total Distance", f"{stats['total_distance_meters']} m")

        col4, col5 = st.columns(2)
        col4.metric("Avg Calories / Session", f"{stats['avg_calories_per_session']} kcal")
        col5.metric("Avg Duration / Session", f"{stats['avg_duration_per_session']} min")

        st.subheader("Stroke Breakdown")
        breakdown_rows = []
        for stroke_name, data in stats["stroke_breakdown"].items():
            breakdown_rows.append({
                "Stroke": stroke_name.capitalize(),
                "Sessions": data["sessions"],
                "Total Calories (kcal)": round(data["calories"], 2),
                "Total Duration (min)": round(data["duration"], 1),
            })
        if breakdown_rows:
            st.dataframe(pd.DataFrame(breakdown_rows), hide_index=True, use_container_width=True)

            # Bar chart for calories by stroke
            chart_df = pd.DataFrame(breakdown_rows).set_index("Stroke")
            st.bar_chart(chart_df["Total Calories (kcal)"])

        st.subheader("Full Report")
        st.code(generate_report(sessions), language=None)

# ── Tab 3: Calorie Calculator ───────────────────────────────────────────────
with tab3:
    st.write("Estimate calories burned without logging a session.")
    c1, c2 = st.columns(2)
    with c1:
        calc_stroke = st.selectbox(
            "Stroke",
            options=list(STROKE_METS.keys()),
            format_func=lambda x: x.capitalize(),
            key="calc_stroke",
        )
        calc_intensity = st.selectbox(
            "Intensity",
            options=["easy", "moderate", "intense"],
            format_func=lambda x: x.capitalize(),
            key="calc_intensity",
        )
    with c2:
        calc_duration = st.number_input("Duration (minutes)", min_value=1.0, value=30.0, step=1.0, key="calc_dur")
        calc_weight = st.number_input("Weight (kg)", min_value=20.0, value=70.0, step=0.5, key="calc_weight")

    calc_calories = calculate_calories(calc_stroke, calc_intensity, calc_duration, calc_weight)
    calc_distance = estimate_distance(calc_stroke, calc_intensity, calc_duration)
    met_val = STROKE_METS[calc_stroke][calc_intensity]

    st.markdown("---")
    rc1, rc2, rc3, rc4 = st.columns(4)
    rc1.metric("MET Value", met_val)
    rc2.metric("Calories Burned", f"{calc_calories} kcal")
    rc3.metric("Estimated Distance", f"{calc_distance} m")
    rc4.metric("Calories / Min", f"{round(calc_calories / calc_duration, 2)} kcal/min")

    st.caption(
        "Formula: Calories = (MET × Weight in kg × Duration in min) / 60. "
        "MET values are based on the Compendium of Physical Activities."
    )

