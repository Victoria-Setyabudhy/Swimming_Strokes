# Swimming Distance and Calorie Tracker

## Run locally

1. Install the requirements.

   ```bash
   pip install -r requirements.txt
   ```

2. Start the app.

   ```bash
   streamlit run streamlit_app.py
   ```

## Authentication flow

When a user creates an account, they must set:

- A password
- A special 4-digit PIN for MFA

On sign-in, the app now asks for:

- Username
- Password
- The special 4-digit PIN

Security notes:

- Username must be 3-32 characters and may contain only letters, numbers, and underscores.
- After repeated failed sign-in attempts, the app temporarily locks sign-in for that username.

Existing users without a saved PIN will be prompted to create one the next time they sign in successfully.
