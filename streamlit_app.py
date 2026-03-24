import streamlit as st
import pandas as pd
import json
import os
import hashlib
from datetime import datetime, timedelta
import calendar

# Custom CSS for ocean gradient background
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #E0F6FF 0%, #B3E5FC 25%, #81D4FA 50%, #4FC3F7 75%, #29B6F6 100%);
        background-attachment: fixed;
    }
    .stApp > header {
        background-color: transparent;
    }
    .stApp .main .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 800px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stApp h1 {
        color: #01579B !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        text-align: center;
        margin-bottom: 1rem !important;
        background: linear-gradient(45deg, #01579B, #0277BD, #0288D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stApp h2, .stApp h3 {
        color: #0277BD;
        font-weight: 600;
    }
    .workout-card {
        background-color: rgba(255, 255, 255, 0.98);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #0277BD;
    }
    .metric-label {
        color: #666 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# Data persistence functions
def load_users():
    if os.path.exists('users.json'):
        try:
            with open('users.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_mfa_code():
    import random
    return ''.join(random.choices('0123456789', k=6))

def load_workouts(username):
    filename = f'workouts_{username}.json'
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_workouts(workouts, username):
    filename = f'workouts_{username}.json'
    with open(filename, 'w') as f:
        json.dump(workouts, f, indent=2, default=str)

# Initialize session state
if 'users' not in st.session_state:
    st.session_state.users = load_users()

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'mfa_code' not in st.session_state:
    st.session_state.mfa_code = None
if 'mfa_username' not in st.session_state:
    st.session_state.mfa_username = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# Login/Register System
if st.session_state.current_user is None:
    st.title("🏊 Swimming Distance and Calorie Tracker")

    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])

    with tab1:
        st.header("Sign In")
        username = st.text_input("Username", key="signin_username")
        password = st.text_input("Password", type="password", key="signin_password")

        if st.button("Sign In"):
            if username in st.session_state.users:
                user_data = st.session_state.users[username]
                if isinstance(user_data, dict) and user_data.get('password_hash') == hash_password(password):
                    # Store user info and ask for email confirmation
                    st.session_state.pending_username = username
                    st.session_state.pending_user_data = user_data
                    st.success("Password verified! Please confirm your email to receive the MFA code.")
                    st.rerun()
                elif isinstance(user_data, str) and user_data == hash_password(password):
                    # Legacy user format - ask for email
                    st.session_state.pending_username = username
                    st.session_state.pending_user_data = {'name': username}  # Legacy format
                    st.success("Password verified! Please enter your email to receive the MFA code.")
                    st.rerun()
                else:
                    st.error("Incorrect password!")
            else:
                st.error("Username not found!")

        # Email confirmation step (shown after password verification)
        if st.session_state.get('pending_username'):
            st.subheader("Confirm Your Email")
            email_input = st.text_input("Enter your email address", key="email_confirm")

            if st.button("Send MFA Code"):
                user_data = st.session_state.pending_user_data
                stored_email = user_data.get('email', '')

                if email_input and email_input == stored_email:
                    # Generate MFA code
                    mfa_code = generate_mfa_code()
                    st.session_state.mfa_code = mfa_code
                    st.session_state.mfa_username = st.session_state.pending_username
                    st.session_state.user_name = user_data.get('name', st.session_state.pending_username)

                    # Clear pending state
                    st.session_state.pending_username = None
                    st.session_state.pending_user_data = None

                    # Simulate sending email
                    st.success(f"MFA code sent to {email_input}")
                    st.info(f"**Demo MFA Code: {mfa_code}** (In production, this would be emailed)")
                    st.rerun()
                elif isinstance(st.session_state.pending_user_data, dict) and not stored_email:
                    # Legacy user - accept any email and store it
                    mfa_code = generate_mfa_code()
                    st.session_state.mfa_code = mfa_code
                    st.session_state.mfa_username = st.session_state.pending_username
                    st.session_state.user_name = user_data.get('name', st.session_state.pending_username)

                    # Update user data with email
                    st.session_state.users[st.session_state.pending_username] = {
                        'password_hash': hash_password(password),
                        'name': user_data.get('name', st.session_state.pending_username),
                        'email': email_input
                    }
                    save_users(st.session_state.users)

                    # Clear pending state
                    st.session_state.pending_username = None
                    st.session_state.pending_user_data = None

                    st.success(f"Email updated! MFA code sent to {email_input}")
                    st.info(f"**Demo MFA Code: {mfa_code}** (In production, this would be emailed)")
                    st.rerun()
                else:
                    st.error("Email address doesn't match our records. Please check and try again.")

        # MFA Code Input (shown after password verification)
        if st.session_state.get('mfa_code') and st.session_state.get('mfa_username'):
            st.subheader("Enter MFA Code")
            entered_code = st.text_input("6-digit code", key="mfa_code_input", max_chars=6)

            if st.button("Verify Code"):
                if entered_code == st.session_state.mfa_code:
                    st.session_state.current_user = st.session_state.mfa_username
                    st.session_state.workouts = load_workouts(st.session_state.current_user)
                    # Clear MFA state
                    st.session_state.mfa_code = None
                    st.session_state.mfa_username = None
                    st.success(f"Welcome back, {st.session_state.user_name}! 🏊‍♀️")
                    st.rerun()
                else:
                    st.error("Invalid MFA code!")

    with tab2:
        st.header("Create Account")
        new_username = st.text_input("Choose Username", key="register_username")
        new_name = st.text_input("Your Full Name", key="register_name")
        new_email = st.text_input("Email Address", key="register_email")
        new_password = st.text_input("Choose Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Create Account"):
            if new_username and new_name and new_email and new_password:
                if new_username in st.session_state.users:
                    st.error("Username already exists!")
                elif new_password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters!")
                elif '@' not in new_email:
                    st.error("Please enter a valid email address!")
                else:
                    st.session_state.users[new_username] = {
                        'password_hash': hash_password(new_password),
                        'name': new_name,
                        'email': new_email
                    }
                    save_users(st.session_state.users)
                    st.session_state.current_user = new_username
                    st.session_state.user_name = new_name
                    st.session_state.workouts = []
                    st.success(f"Account created successfully! Welcome, {new_name}! 🏊‍♀️")
                    st.rerun()
            else:
                st.error("Please fill in all fields!")

    #else:
    # Main App (only shown when logged in)

# Create tabs
tab1, tab2 = st.tabs(["🏊 Log Workout", "📊 Workout History"])

with tab1:
    st.header("Enter Your Swim Details")

    # Number of laps
    laps = st.number_input("Number of Laps", min_value=0, value=0, step=1)

    # Pool length
    pool_options = ["25 meters", "25 yards", "50 meters"]
    pool_length_str = st.selectbox("Pool Length", pool_options)

    # Parse pool length
    if "meters" in pool_length_str:
        pool_length = int(pool_length_str.split()[0])
        unit = "meters"
    elif "yards" in pool_length_str:
        pool_length = int(pool_length_str.split()[0])
        unit = "yards"

    # Stroke
    stroke_options = ["Freestyle", "Backstroke", "Breaststroke", "Butterfly"]
    stroke = st.selectbox("Stroke", stroke_options)

    # Weight for calories
    weight_unit = st.selectbox("Weight Unit", ["kg", "lbs"])
    weight = st.number_input(f"Your Weight ({weight_unit})", min_value=0.0, value=70.0 if weight_unit == "kg" else 154.0, step=0.1)

    # Convert weight to kg if in lbs
    if weight_unit == "lbs":
        weight_kg = weight * 0.453592
    else:
        weight_kg = weight

    # Date
    workout_date = st.date_input("Workout Date", datetime.now().date())

    # Calculations and Save
    if laps > 0:
        # Distance
        distance = laps * pool_length
        st.subheader(f"Total Distance: {distance} {unit}")

        # Convert to meters for calorie calculation
        if unit == "yards":
            distance_m = distance * 0.9144
        else:
            distance_m = distance

        # MET values (approximate)
        met_values = {
            "Freestyle": 8.0,
            "Backstroke": 7.0,
            "Breaststroke": 6.0,
            "Butterfly": 9.0
        }
        met = met_values[stroke]

        # Average speeds (m/s)
        speeds = {
            "Freestyle": 1.5,
            "Backstroke": 1.3,
            "Breaststroke": 1.2,
            "Butterfly": 1.4
        }
        speed = speeds[stroke]

        # Time in hours
        time_hours = distance_m / speed / 3600

        # Calories
        calories = met * weight_kg * time_hours
        st.subheader(f"Estimated Calories Burned: {calories:.1f}")

        # Save workout button
        if st.button("💾 Save Workout"):
            workout = {
                "date": workout_date.isoformat(),
                "laps": laps,
                "pool_length": pool_length,
                "unit": unit,
                "stroke": stroke,
                "weight_kg": weight_kg,
                "distance": distance,
                "calories": round(calories, 1),
                "time_hours": time_hours
            }
            st.session_state.workouts.append(workout)
            save_workouts(st.session_state.workouts, st.session_state.current_user)
            st.success("Workout saved successfully! 🎉")

            # Confetti animation
            st.balloons()
            st.markdown("""
            <script>
                // Confetti falling effect
                function createConfetti() {
                    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b', '#6c5ce7', '#a29bfe', '#fd79a8', '#00b894'];
                    for (let i = 0; i < 100; i++) {
                        const confetti = document.createElement('div');
                        confetti.style.position = 'fixed';
                        confetti.style.width = Math.random() * 8 + 4 + 'px';
                        confetti.style.height = Math.random() * 8 + 4 + 'px';
                        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                        confetti.style.left = Math.random() * 100 + 'vw';
                        confetti.style.top = '-20px';
                        confetti.style.zIndex = '9999';
                        confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
                        confetti.style.animation = 'confettiFall ' + (Math.random() * 2 + 3) + 's linear forwards';
                        confetti.style.transform = 'rotate(' + Math.random() * 360 + 'deg)';
                        document.body.appendChild(confetti);

                        setTimeout(() => {
                            if (document.body.contains(confetti)) {
                                document.body.removeChild(confetti);
                            }
                        }, 5000);
                    }
                }

                // Add keyframes for confetti animation
                const style = document.createElement('style');
                style.textContent = `
                    @keyframes confettiFall {
                        0% {
                            transform: translateY(-20px) rotate(0deg);
                            opacity: 1;
                        }
                        100% {
                            transform: translateY(100vh) rotate(720deg);
                            opacity: 0;
                        }
                    }
                `;
                document.head.appendChild(style);

                createConfetti();
            </script>
            """, unsafe_allow_html=True)

        # Note
        st.write("*Estimates are approximate and based on average speeds and MET values. Actual calories may vary based on intensity, fitness level, and other factors.*")
    else:
        st.write("Enter the number of laps to see calculations.")

with tab2:
    st.header("Your Workout History")

    if st.session_state.workouts:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(st.session_state.workouts)
        df['date'] = pd.to_datetime(df['date'])

        # Filter by year
        years = sorted(df['date'].dt.year.unique(), reverse=True)
        selected_year = st.selectbox("Select Year", years if years else [datetime.now().year])

        # Filter data for selected year
        year_data = df[df['date'].dt.year == selected_year]

        if not year_data.empty:
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_distance = year_data['distance'].sum()
                total_unit = year_data['unit'].iloc[0]  # Assuming consistent units
                st.metric("Total Distance", f"{total_distance} {total_unit}")
            with col2:
                total_calories = year_data['calories'].sum()
                st.metric("Total Calories", f"{total_calories:.1f}")
            with col3:
                total_workouts = len(year_data)
                st.metric("Total Workouts", total_workouts, delta_color="off")

            # Monthly breakdown
            st.subheader("Monthly Summary")
            year_data['month'] = year_data['date'].dt.month
            monthly = year_data.groupby('month').agg({
                'distance': 'sum',
                'calories': 'sum',
                'date': 'count'
            }).rename(columns={'date': 'workouts'})

            # Fill missing months
            all_months = pd.DataFrame(index=range(1, 13))
            monthly = all_months.join(monthly).fillna(0)

            # Month names
            monthly['month_name'] = monthly.index.map(lambda x: calendar.month_name[x])

            # Display monthly data
            st.dataframe(monthly[['month_name', 'distance', 'calories', 'workouts']].rename(
                columns={'month_name': 'Month', 'distance': f'Distance ({total_unit})', 'calories': 'Calories', 'workouts': 'Workouts'}
            ), use_container_width=True)

            # Recent workouts
            st.subheader("Recent Workouts")
            recent = year_data.sort_values('date', ascending=False).head(10)
            for _, workout in recent.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="workout-card">
                        <strong>{workout['date'].strftime('%B %d, %Y')}</strong><br>
                        {workout['distance']} {workout['unit']} • {workout['stroke']} • {workout['calories']:.1f} calories
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.write(f"No workouts found for {selected_year}.")
    else:
        st.write("No workouts saved yet. Start logging your swims!")

    # Clear all data button
    if st.session_state.workouts and st.button("🗑️ Clear All Workout Data"):
        st.session_state.workouts = []
        save_workouts([])
        st.success("All workout data cleared!")
        st.rerun()
