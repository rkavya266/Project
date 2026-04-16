from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import pickle
import numpy as np
import pandas as pd
import warnings
import json
import os
import hashlib
import uuid
from datetime import datetime
warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = "finsight_secret_key_change_in_production"

# ── JSON "Database" helpers ────────────────────────────────────────────────────
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ── Load ML Models ─────────────────────────────────────────────────────────────
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("kmeans.pkl", "rb") as f:
    kmeans = pickle.load(f)

PRODUCTS = ["Investment", "Loan", "Credit Score", "Savings", "EMI"]
PRODUCT_ICONS = {
    "Investment": "📈",
    "Loan": "🏦",
    "Credit Score": "💳",
    "Savings": "🏧",
    "EMI": "📅"
}
PRODUCT_DESC = {
    "Investment": "Grow your wealth through diversified portfolios and market-linked instruments tailored to your risk appetite.",
    "Loan": "Access flexible credit facilities at competitive rates matching your repayment capacity.",
    "Credit Score": "Build and improve your credit profile for better financial opportunities and lower interest rates.",
    "Savings": "Maximize returns on idle funds with high-yield savings accounts and fixed deposits.",
    "EMI": "Structure purchases with manageable installment plans that fit your monthly cash flow."
}

FEATURE_COLUMNS = [
    "Age", "Income", "Credit_Score", "Monthly_Expenses",
    "Savings", "Loan_Amount", "Savings_Ratio",
    "Expense_Ratio", "Net_Disposable_Income"
]

# ── Auth helpers ───────────────────────────────────────────────────────────────
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    users = load_json(USERS_FILE)
    return users.get(uid)

def require_login(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"success": False, "error": "Not authenticated"}), 401
    return decorated

# ── Routes: Pages ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("index.html")

@app.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/profile")
def profile_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("profile.html")

# ── Routes: Auth API ───────────────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"success": False, "error": "All fields are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters."}), 400

    users = load_json(USERS_FILE)

    # Check duplicate email
    for u in users.values():
        if u["email"] == email:
            return jsonify({"success": False, "error": "Email already registered."}), 400

    uid = str(uuid.uuid4())
    users[uid] = {
        "id": uid,
        "name": name,
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        # Pre-fill profile fields (empty initially)
        "profile": {
            "age": "", "gender": "", "education": "",
            "employment": "", "income": "", "monthly_expenses": "",
            "savings": "", "loan_amount": "", "credit_score": ""
        }
    }
    save_json(USERS_FILE, users)

    session["user_id"] = uid
    return jsonify({"success": True, "name": name})


@app.route("/api/login", methods=["POST"])
def login():
    data     = request.json
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    users = load_json(USERS_FILE)
    for uid, u in users.items():
        if u["email"] == email and u["password"] == hash_password(password):
            session["user_id"] = uid
            return jsonify({"success": True, "name": u["name"]})

    return jsonify({"success": False, "error": "Invalid email or password."}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/me")
def me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"success": False}), 401
    users = load_json(USERS_FILE)
    u = users.get(uid)
    if not u:
        return jsonify({"success": False}), 401
    return jsonify({
        "success": True,
        "name": u["name"],
        "email": u["email"],
        "created_at": u["created_at"],
        "profile": u.get("profile", {})
    })


@app.route("/api/profile", methods=["POST"])
def update_profile():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"success": False, "error": "Not authenticated"}), 401

    users = load_json(USERS_FILE)
    u = users.get(uid)
    if not u:
        return jsonify({"success": False, "error": "User not found"}), 404

    data = request.json
    allowed = ["age", "gender", "education", "employment",
               "income", "monthly_expenses", "savings", "loan_amount", "credit_score"]

    for field in allowed:
        if field in data:
            u["profile"][field] = data[field]

    # Allow name update
    if "name" in data and data["name"].strip():
        u["name"] = data["name"].strip()

    save_json(USERS_FILE, users)
    return jsonify({"success": True, "profile": u["profile"], "name": u["name"]})


# ── Routes: History API ────────────────────────────────────────────────────────
@app.route("/api/history")
def history():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    all_history = load_json(HISTORY_FILE)
    user_history = all_history.get(uid, [])
    # Return latest 10 entries
    return jsonify({"success": True, "history": user_history[-10:][::-1]})


# ── Routes: Predict ────────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    uid = session.get("user_id")
    data = request.json
    try:
        age              = float(data["age"])
        income           = float(data["income"])
        loan_amount      = float(data["loan_amount"])
        credit_score     = float(data["credit_score"])
        savings          = float(data["savings"])
        gender           = int(data["gender"])
        education        = int(data["education"])
        employment       = int(data["employment"])
        monthly_expenses = float(data["monthly_expenses"])

        # Derived features
        emi              = loan_amount / 60 if loan_amount > 0 else 0
        debt_to_income   = loan_amount / income if income > 0 else 0
        savings_ratio    = savings / income if income > 0 else 0
        expense_ratio    = monthly_expenses / income if income > 0 else 0
        net_disposable   = income - monthly_expenses
        risk_score       = (debt_to_income * 0.4 + expense_ratio * 0.3 + (1 - savings_ratio) * 0.3)

        input_df = pd.DataFrame([{
            "Age": age, "Income": income, "Credit_Score": credit_score,
            "Monthly_Expenses": monthly_expenses, "Savings": savings,
            "Loan_Amount": loan_amount, "Savings_Ratio": savings_ratio,
            "Expense_Ratio": expense_ratio, "Net_Disposable_Income": net_disposable
        }])
        input_df = input_df[FEATURE_COLUMNS]

        preds   = model.predict(input_df)[0]
        cluster = int(kmeans.predict(input_df)[0])

        results = []
        for product, score in zip(PRODUCTS, preds):
            pct = round(float(score) * 100, 1)
            pct = max(0, min(100, pct))
            results.append({
                "product": product,
                "icon": PRODUCT_ICONS[product],
                "score": pct,
                "description": PRODUCT_DESC[product]
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        top2   = results[:2]
        others = results[2:]

        derived = {
            "emi": round(emi, 2),
            "debt_to_income": round(debt_to_income * 100, 1),
            "savings_ratio": round(savings_ratio * 100, 1),
            "expense_ratio": round(expense_ratio * 100, 1),
            "net_disposable": round(net_disposable, 2),
            "risk_score": round(risk_score, 3)
        }

        # Save prediction to history if logged in
        if uid:
            all_history = load_json(HISTORY_FILE)
            if uid not in all_history:
                all_history[uid] = []
            all_history[uid].append({
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "inputs": {
                    "age": age, "income": income, "loan_amount": loan_amount,
                    "credit_score": credit_score, "savings": savings,
                    "monthly_expenses": monthly_expenses
                },
                "top_recommendation": top2[0]["product"] if top2 else "",
                "cluster": cluster,
                "derived": derived
            })
            # Keep only last 50 entries per user
            all_history[uid] = all_history[uid][-50:]
            save_json(HISTORY_FILE, all_history)

            # Also auto-save inputs to profile
            users = load_json(USERS_FILE)
            if uid in users:
                users[uid]["profile"].update({
                    "age": str(int(age)), "income": str(int(income)),
                    "loan_amount": str(int(loan_amount)), "credit_score": str(int(credit_score)),
                    "savings": str(int(savings)), "monthly_expenses": str(int(monthly_expenses)),
                    "gender": str(gender), "education": str(education), "employment": str(employment)
                })
                save_json(USERS_FILE, users)

        return jsonify({
            "success": True,
            "top": top2,
            "others": others,
            "cluster": cluster,
            "derived": derived
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
