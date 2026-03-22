# 🏡 Real Estate Investment Analysis Tool

An AI-powered web application that helps users analyze real estate investments using machine learning, financial metrics, and risk simulations.

---

## 🚀 Overview

This project combines predictive analytics, financial modeling, and AI decision-making to assist users in making smarter real estate investment decisions.

---

## ✨ Features

- Property price prediction using Machine Learning  
- ROI, IRR, NOI, and Cashflow calculations  
- Monte Carlo risk analysis  
- AI-based investment score  
- Smart recommendation system (BUY / HOLD / AVOID)  
- Admin dashboard with analytics  

---

## 🛠️ Tech Stack

- Backend: Flask, Python  
- ML: Scikit-learn, Pandas, NumPy  
- Frontend: HTML, CSS, Bootstrap, JavaScript  
- Charts: Chart.js  
- Database: SQLite  

---

## 📊 System Workflow

```mermaid
flowchart TD

A[User Input] --> B[ML Price Prediction]
B --> C[Financial Analysis - ROI IRR NOI]
C --> D[Risk Simulation - Monte Carlo]
D --> E[AI Investment Score]
E --> F[Recommendation - BUY HOLD AVOID]

F --> G[User Dashboard]
F --> H[Admin Dashboard]

G --> I[Store Data in Database]
H --> I
```

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/Unnati310559/Real-Estate-WebApp.git

cd Real-Estate-WebApp
```

### 2️⃣ Install dependencies

```
pip install -r requirements.txt

```

### 3️⃣ Run the application
```

python app.py

```

### 4️⃣ Open in browser
```

http://127.0.0.1:5001

```

## 📌 Project Workflow Explanation

1. User enters property and financial details  
2. Machine Learning model predicts property price  
3. Financial metrics (ROI, IRR, NOI, Cashflow) are calculated  
4. Risk is analyzed using Monte Carlo simulation  
5. AI generates an investment score  
6. System provides recommendation (BUY / HOLD / AVOID)  
7. Data is stored and displayed on dashboard  

---

## 🔐 Security Features

- Password hashing  
- Session-based authentication  
- Basic input validation  

---

## ⚠️ Limitations

- Uses US housing dataset (King County)  
- Rent values are user-provided  
- No real-time market integration  

---

## 🚀 Future Improvements

- Property comparison tool  
- Market trend prediction  
- Portfolio analysis  
- Email notifications  
- Multi-language support  

---

## 👩‍💻 Contributors

- Unnati Gupta  
- Vedant Agrawal  
- Aditya Verma  

---

## 📌 Status

✔ MVP Complete  
✔ Beta Ready  

---

## ⭐ If you like this project, give it a star!
