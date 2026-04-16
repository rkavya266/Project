FinSight — Personalized Financial Product Recommendation
ML-Powered Web Application
📁 Project Structure
finrec/
├── app.py                  ← Flask backend (API + routing)
├── model.pkl               ← Trained Multi-Output Regression Model
├── kmeans.pkl              ← User Segmentation Model
├── history.json            ← Stores user recommendation history
├── user.json               ← Stores user login & profile data
├── requirements.txt        ← Python dependencies
├── templates/
│   └── index.html          ← Frontend (HTML/CSS/JS)
└── README.md
⚙️ Setup Instructions
1. Install Dependencies
pip install -r requirements.txt

⚠️ Important: Ensure the same scikit-learn version used during training (recommended: 1.6.1)

2. Place Model Files

Download the trained models:

📦 Model:

model.pkl link: https://drive.google.com/file/d/18c2tTMDPjBXfhLlaTP6U9uNthY5-s6Yh/view?usp=sharing

kmeans.pkl link: https://drive.google.com/file/d/1D_qLMs_Ou9RFuY69dTcv5CE3eFU6Qvdk/view?usp=sharing

Place both files in the root directory:

model.pkl
kmeans.pkl

3. Run the App
python app.py
4. Open in Browser

Visit: http://localhost:5000

🧠 Model Details
| Property       | Value                        |
| -------------- | ---------------------------- |
| Model Type     | MultiOutputRegressor         |
| Base Estimator | RandomForestRegressor        |
| Clustering     | KMeans (3 segments)          |
| Approach       | Hybrid Recommendation System |
| Input Features | 15 features                  |
| Output Targets | 5 financial product scores   |


📊 Techniques Used

1. Regression Model (Core Engine)
Predicts continuous suitability scores (0–1) for each product
Enables ranking-based recommendation

2. Clustering (User Segmentation)
Groups users into financial categories
Helps identify:
Low-income users
High savers
High-risk borrowers

3. Rule-Based System

Adds financial logic such as:

Low credit score → Avoid loans
High savings → Suggest investments
High expenses → Reduce spending

4. Hybrid Recommendation System

Final output combines:
ML Predictions (Regression)
User Segment (Clustering)
Financial Rules (Domain Knowledge)

📥 Input Features
| Feature               | Source     |
| --------------------- | ---------- |
| Age                   | User input |
| Income                | User input |
| Loan Amount           | User input |
| Credit Score          | User input |
| Savings               | User input |
| Gender                | User input |
| Education Level       | User input |
| Employment Status     | User input |
| Monthly Expenses      | User input |
| EMI                   | Derived    |
| Debt-to-Income Ratio  | Derived    |
| Savings Ratio         | Derived    |
| Expense Ratio         | Derived    |
| Net Disposable Income | Derived    |
| Risk Score            | Derived    |

📤 Output Products (% Suitability)
Investment Priority
Loan Priority
Credit Score Priority
Savings Priority
EMI Eligibility

🔄 How It Works
User logs in and enters financial details
Data is stored in user.json
Flask backend computes derived features
Regression model predicts product suitability scores
KMeans assigns user cluster
Rule-based system adds financial insights
Top 2 recommendations are displayed

Results are saved in history.json
💡 Derived Feature Formulas
EMI              = loan_amount / 60
Debt-to-Income   = loan_amount / income
Savings Ratio    = savings / income
Expense Ratio    = monthly_expenses / income
Net Disposable   = income - monthly_expenses
Risk Score       = (debt_to_income × 0.4) + 
                   (expense_ratio × 0.3) + 
                   ((1 - savings_ratio) × 0.3)
🗂 Data Storage (Without Database)
user.json

Stores:
User credentials
Profile information
history.json

Stores:
Previous recommendations
Input values
Derived metrics
Top recommendations

🚀 Future Enhancements
Database integration (MySQL / MongoDB)
Authentication system with JWT
Personalized dashboards
Explainable AI (feature importance per user)
Real-time financial product APIs

 Authors:
Mathumitha DR
Kavya Ravichandran
