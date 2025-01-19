from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session,
)
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from typing_extensions import TypedDict
import sqlite3
import re
import json
import google.generativeai as genai
import risk_factors
from constants import GOOGLE_API_KEY, FLASK_SECRET_KEY

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Gemini API configuration
genai.configure(api_key=GOOGLE_API_KEY)


def is_valid_password(password: str) -> Optional[str]:
    """Password validation function."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return 'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).'
    return None


def calculate_score(parsed_results: dict) -> int:
    """
    Calculate the total risk score based on parsed results.

    Args:
        parsed_results (dict): A dictionary containing risk factors and their details.

    Returns:
        int: The total risk score calculated based on the risk levels.
    """
    scores = {"very high risk": 10, "high risk": 8, "medium risk": 5, "low risk": 1}
    total_score = 0
    for factor, details in parsed_results.items():
        if isinstance(details, dict):  # Ensure details is a dictionary
            risk_level = details.get("risk_level", "").lower()
            total_score += scores.get(risk_level, 0)
        else:
            print(f"Skipping {factor} as details are not a dictionary: {details}")
    return total_score


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route."""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if not username or not email or not password:
            flash("All fields are required!")
            return redirect(url_for("register"))

        # Validate password
        password_error = is_valid_password(password)
        if password_error:
            flash(password_error)
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password, method="pbkdf2:sha256")

        conn = None
        try:
            conn = sqlite3.connect("risk_assessment.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            conn.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists. Please use a different one.")
            return redirect(url_for("register"))
        finally:
            if conn:
                conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Both username and password are required!")
            return redirect(url_for("login"))

        try:
            conn = sqlite3.connect("risk_assessment.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, password_hash FROM users WHERE username = ?", (username,)
            )
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user[1], password):
                session["user_id"] = user[0]
                session["username"] = username
                flash("Login successful! Welcome back.")
                return redirect(url_for("assessment"))
            else:
                flash("Invalid username or password.")
                return redirect(url_for("login"))

        except sqlite3.Error as e:
            flash("Database error occurred. Please try again later.")
            print(e)
            return redirect(url_for("login"))

    return render_template("login.html")


def login_required(f):
    """Login required decorator."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/logout")
def logout():
    """User logout route."""
    session.clear()
    flash("You have been logged out successfully.")
    return redirect(url_for("landing"))


@app.route("/")
def landing():
    """Landing page route."""
    return render_template("landing.html")


@app.route("/assessment", methods=["GET"])
@login_required
def assessment():
    """Assessment path (protected) with chat interface."""
    return render_template("chat.html")


@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    """Route to process user input and return risk assessment."""
    messages = []

    user_input = request.json.get("description", "")
    history = request.json.get("history", [])

    # Validate input
    if not user_input:
        return jsonify({"error": "No description provided"}), 400

    # Reconstruct messages from history
    messages = history if history else []

    try:
        found_answers = False
        while not found_answers:
            prompt = "\n".join(
                [f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages]
            )
            prompt += f"""
            This is a task in which you will be asked to play the role of a legal advisor. 
            
            Specifically, a user is providing the above description of an AI product that a client or company is considering to use.
    
            Assign a risk level for the AI product ("very high risk", "high risk", "medium risk", or "low risk") for each of the ten risk factors: 
            1. Users and Audience; 
            2. Use and Functionality; 
            3. Data Processed; 
            4. Legal and Regulatory Compliance, 
            5. Transparency; 
            6. Technology; 
            7. Bias and Fairness; 
            8. Operational Risk; 
            9. Training Data; 
            10. Reputational Risk.
            
            The criteria for each level for each risk factor are described below to help inform your assessment: {risk_factors.RISK_FACTORS}
    
            If you are unsure about the majority of the factors and need more information to assign a level to the risk factors, please return:
            up to 3 simple clarifying questions on the most unclear topics to the user by providing a string under 'clarifying_question'. 
            Don't ask clarifying questions for factors for which you have information.
    
            If you have enough information to make an assessment (including based on what you think is the likely remaining context), please provide:
            - a risk level for each of the 10 factors (ideally, there would be a variety of levels - including some "low", some "medium" and some "high" or "very high" risk factors);
            - justification for each risk level (a few sentences for each factor); and
            - leave the clarifying questions empty.
    
            """

            # Call LLM
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                contents=[prompt],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=risk_factors.RiskAssessment,
                ),
            )

            # Parse response
            result = response.text
            parsed_result = json.loads(result)
            clarifying_questions = parsed_result.get("clarifying_questions", [])
            # Handle clarifying questions
            if clarifying_questions:
                # Count clarifying question rounds
                clarifying_rounds = sum(
                    1 for message in history if message["role"] == "assistant"
                )
                if clarifying_rounds <= 2:
                    # Add clarifying questions to messages
                    messages.append(
                        {"role": "assistant", "content": " ".join(clarifying_questions)}
                    )
                    return jsonify(
                        {
                            "clarifying_questions": clarifying_questions,
                            "history": messages,
                        }
                    )
                else:
                    found_answers = True
            else:
                # If no clarifying questions, redirect to the results page
                found_answers = True
        if found_answers:
            session["parsed_results"] = parsed_result  # Store in session

            def format_messages(messages):
                return [
                    {"role": msg["role"], "content": msg["content"]} for msg in messages
                ]

            session["conversation_history"] = format_messages(messages)
            
            # Redirect to the results page
            return jsonify({"redirect_url": url_for("results")})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/results")
@login_required
def results():
        
    """Results page route."""
    # Retrieve stored data from session
    parsed_results = session.get("parsed_results", {})
    conversation_history = session.get("conversation_history", [])
    if not parsed_results:
        flash("No results found. Please try again.", "error")
        return redirect(url_for("assessment"))

    total_score = calculate_score(parsed_results)
    if total_score > 80:
        final_assessment = "Very High Risk"
    elif total_score > 60:
        final_assessment = "High Risk"
    elif total_score > 30:
        final_assessment = "Medium Risk"
    else:
        final_assessment = "Low Risk"
             
    try:

        prompt = f"""
            f"You are a lawyer. You have obtained from the client the following information on an AI tool "
            f"that a client or company is considering to use: {conversation_history}. "
            f"Based on the risk factors provided, you have assessed the AI tool to have a {final_assessment} "
            f"level of risk with a score out of 100 of {total_score}. Your full analysis against 10 factors is here: {parsed_results}. "
            f"Please provide: a brief summary containing a one sentence summary of what you understand the proposed AI tool to be; "
            f"a maximum 4 sentences of why you have attributed the final assessment level of risk based on the risk factors; "
            f"and recommendations to mitigate the key risks.
            """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            contents=[prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=risk_factors.Summary
            ),
        )
        # Parse response
        summary_text = response.text
        summary = json.loads(summary_text)
    
    except Exception as e:
        summary = f"An error occurred while generating the summary: {str(e)}"


    return render_template(
        "results.html",
        parsed_results=parsed_results,
        total_score=total_score,
        final_assessment=final_assessment,
        summary=summary,
    )

def init_db():
    conn = sqlite3.connect("risk_assessment.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """
    )
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False)
