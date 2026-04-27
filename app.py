from flask import Flask, render_template, request, redirect, url_for, jsonify
from services.prediction import predict_price
from services.financial import calculate_noi, calculate_cap_rate, calculate_cashflow, calculate_roi, calculate_irr
from services.risk import monte_carlo_simulation, calculate_risk_score
from services.recommendation import generate_recommendation
from services.investment_score import calculate_investment_score
from groq import Groq

from database import db, User, Analysis, Property

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
load_dotenv()
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__, template_folder='templates')

# =========================
# CONFIG (SECURE)
# =========================
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "devkey")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///realestate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# =========================
# LOGIN MANAGER
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# =========================
# HOME
# =========================
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("home.html")

# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        import re

        username = request.form.get("username")
        password = request.form.get("password")

        # ✅ Basic validation
        if not username or not password:
            return render_template("register.html", error="Invalid input")

        # 🔐 PASSWORD REGEX VALIDATION
        PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"

        if not re.match(PASSWORD_REGEX, password):
            return render_template(
                "register.html",
                error="Password must be 8+ chars with uppercase, lowercase, number & special character"
            )

        # ✅ Check existing user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", error="User already exists!")

        # ✅ Assign role
        role = "admin" if username == "admin" else "user"

        # ✅ Hash password
        hashed_password = generate_password_hash(password)

        # ✅ Save user
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("dashboard"))

        return "Invalid Credentials"

    return render_template("login.html")

# =========================
# LOGOUT
# =========================


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# =========================
# ANALYZE
# =========================
@app.route("/analyze", methods=["POST"])
@login_required
def analyze():

    try:
        # =============================
        # INPUT VALIDATION
        # =============================
        annual_rent = float(request.form.get("annual_rent", 0))
        annual_expenses = float(request.form.get("annual_expenses", 0))
        annual_loan_payment = float(request.form.get("annual_loan_payment", 0))
        years = int(request.form.get("years", 0))

        if annual_rent <= 0 or annual_expenses < 0 or years <= 0:
            return "Invalid financial input"

        bedrooms = int(request.form.get("bedrooms", 0))
        bathrooms = float(request.form.get("bathrooms", 0))
        sqft_living = int(request.form.get("sqft_living", 0))

        if bedrooms <= 0 or bathrooms <= 0 or sqft_living <= 0:
            return "Invalid property data"

        grade = int(request.form.get("grade", 0))
        condition = int(request.form.get("condition", 0))
        yr_built = int(request.form.get("yr_built", 0))
        lat = float(request.form.get("lat", 0))
        long = float(request.form.get("long", 0))
        year_sold = int(request.form.get("year_sold", 0))

        # =============================
        # SAVE PROPERTY
        # =============================
        property_obj = Property(
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            sqft_living=sqft_living,
            grade=grade,
            condition=condition,
            yr_built=yr_built,
            latitude=lat,
            longitude=long,
            year_sold=year_sold
        )

        db.session.add(property_obj)
        db.session.commit()

        # =============================
        # PREDICTION
        # =============================
        property_data = {
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "sqft_living": sqft_living,
            "grade": grade,
            "condition": condition,
            "yr_built": yr_built,
            "lat": lat,
            "long": long,
            "year_sold": year_sold
        }

        # =============================
        # PREDICTION (WITH CORRECTION LAYER)
        # =============================

        predicted_price_usd = predict_price(property_data)

        # Step 1: USD → INR
        price_inr = predicted_price_usd * 93

        # Step 2: Indian market correction
        if sqft_living > 3000:
            correction_factor = 0.35
        elif sqft_living > 1500:
            correction_factor = 0.4
        else:
            correction_factor = 0.45

        predicted_price = price_inr * correction_factor

        # Step 3: Realistic Indian rental yield
        suggested_rent = predicted_price * 0.06

        # =============================
        # FINANCIALS
        # =============================
        noi = calculate_noi(annual_rent, annual_expenses)
        cap_rate = calculate_cap_rate(noi, predicted_price)
        cashflow = calculate_cashflow(annual_rent, annual_expenses, annual_loan_payment)
        roi = calculate_roi(cashflow * years, predicted_price)
        irr = calculate_irr(predicted_price, cashflow, years)

        # =============================
        # RISK + RECOMMENDATION
        # =============================
        simulated = monte_carlo_simulation(roi / 100, 0.05)
        risk_result = calculate_risk_score(simulated)

        investment_score = calculate_investment_score(roi, irr, risk_result["risk_level"])

        recommendation = generate_recommendation(roi, irr, risk_result["risk_level"])

        # =============================
        # SAVE ANALYSIS
        # =============================
        new_analysis = Analysis(
            annual_rent=annual_rent,
            annual_expenses=annual_expenses,
            annual_loan_payment=annual_loan_payment,
            investment_years=years,
            predicted_price=predicted_price,
            roi=roi,
            irr=irr,
            risk_level=risk_result["risk_level"],
            recommendation=recommendation,
            investment_score=investment_score,
            user_id=current_user.id,
            property_id=property_obj.id
        )

        db.session.add(new_analysis)
        db.session.commit()

        # =============================
        # RESULT
        # =============================
        return render_template(
            "result.html",
            predicted_price=predicted_price,
            noi=noi,
            cap_rate=cap_rate,
            cashflow=cashflow,
            roi=roi,
            irr=irr,
            risk=risk_result,
            recommendation=recommendation,
            investment_score=investment_score,
            suggested_rent=suggested_rent,
            simulated_returns=simulated.tolist() if hasattr(simulated, "tolist") else simulated
        )

    except Exception as e:
        return f"Error: {str(e)}"

# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
@login_required
def dashboard():
    analyses = Analysis.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", analyses=analyses)


@app.route("/analysis-form")
@login_required
def analysis_form():
    return render_template("index.html")

# =========================
# DELETE ANALYSIS
# =========================
@app.route("/delete-analysis/<int:id>", methods=["POST"])
@login_required
def delete_analysis(id):
    analysis = Analysis.query.get(id)

    if not analysis or analysis.user_id != current_user.id:
        return "Unauthorized"

    db.session.delete(analysis)
    db.session.commit()

    return redirect(url_for("dashboard"))

# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        return "Access Denied"

    total_users = User.query.count()
    total_analysis = Analysis.query.count()

    analyses = Analysis.query.all()

    roi_list = [a.roi for a in analyses]
    price_list = [a.predicted_price for a in analyses]

    risk_counts = {"Low": 0, "Medium": 0, "High": 0}
    for a in analyses:
        if a.risk_level in risk_counts:
            risk_counts[a.risk_level] += 1

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_analysis=total_analysis,
        analyses=analyses,
        roi_list=roi_list,
        price_list=price_list,
        risk_counts=risk_counts
    )


@app.route("/api/analyze", methods=["POST"])
@login_required
def analyze_api():
    try:
        data = request.get_json()

        # Input validation
        annual_rent = float(data.get("annual_rent", 0))
        annual_expenses = float(data.get("annual_expenses", 0))
        annual_loan_payment = float(data.get("annual_loan_payment", 0))
        years = int(data.get("years", 0))

        if annual_rent <= 0 or annual_expenses < 0 or years <= 0:
            return jsonify({"error": "Invalid financial input"}), 400

        bedrooms = int(data.get("bedrooms", 0))
        bathrooms = float(data.get("bathrooms", 0))
        sqft_living = int(data.get("sqft_living", 0))

        if bedrooms <= 0 or bathrooms <= 0 or sqft_living <= 0:
            return jsonify({"error": "Invalid property data"}), 400

        # Property creation
        property_obj = Property(
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            sqft_living=sqft_living,
            grade=int(data.get("grade", 0)),
            condition=int(data.get("condition", 0)),
            yr_built=int(data.get("yr_built", 0)),
            latitude=float(data.get("lat", 0)),
            longitude=float(data.get("long", 0)),
            year_sold=int(data.get("year_sold", 0))
        )

        db.session.add(property_obj)
        db.session.commit()

        # Prediction
        property_data = {
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "sqft_living": sqft_living,
            "grade": property_obj.grade,
            "condition": property_obj.condition,
            "yr_built": property_obj.yr_built,
            "lat": property_obj.latitude,
            "long": property_obj.longitude,
            "year_sold": property_obj.year_sold
        }

        predicted_price_usd = predict_price(property_data)

        price_inr = predicted_price_usd * 93

        if sqft_living > 3000:
            correction_factor = 0.35
        elif sqft_living > 1500:
            correction_factor = 0.4
        else:
            correction_factor = 0.45

        predicted_price = price_inr * correction_factor

        suggested_rent = predicted_price * 0.06

        # Financials
        noi = calculate_noi(annual_rent, annual_expenses)
        cap_rate = calculate_cap_rate(noi, predicted_price)
        cashflow = calculate_cashflow(annual_rent, annual_expenses, annual_loan_payment)
        roi = calculate_roi(cashflow * years, predicted_price)
        irr = calculate_irr(predicted_price, cashflow, years)

        # Risk
        simulated = monte_carlo_simulation(roi / 100, 0.05)
        risk_result = calculate_risk_score(simulated)

        investment_score = calculate_investment_score(roi, irr, risk_result["risk_level"])
        recommendation = generate_recommendation(roi, irr, risk_result["risk_level"])

        # Save analysis
        new_analysis = Analysis(
            annual_rent=annual_rent,
            annual_expenses=annual_expenses,
            annual_loan_payment=annual_loan_payment,
            investment_years=years,
            predicted_price=predicted_price,
            roi=roi,
            irr=irr,
            risk_level=risk_result["risk_level"],
            recommendation=recommendation,
            investment_score=investment_score,
            user_id=current_user.id,
            property_id=property_obj.id
        )

        db.session.add(new_analysis)
        db.session.commit()

        return jsonify({
            "predicted_price": predicted_price,
            "noi": noi,
            "cap_rate": cap_rate,
            "cashflow": cashflow,
            "roi": roi,
            "irr": irr,
            "risk": risk_result,
            "recommendation": recommendation,
            "investment_score": investment_score,
            "suggested_rent": suggested_rent
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route("/compare")
@login_required
def compare_page():
    return render_template("compare.html")


@app.route("/api/compare", methods=["POST"])
@login_required
def compare_properties():

    data = request.get_json()

    def analyze(prop):

        property_data = {
            "bedrooms": 2,
            "bathrooms": 1,
            "sqft_living": prop["sqft_living"],
            "grade": 5,
            "condition": 3,
            "yr_built": 2000,
            "lat": 0,
            "long": 0,
            "year_sold": 2020
        }

        price = predict_price(property_data) * 93 * 0.4

        noi = calculate_noi(prop["rent"], prop["expenses"])
        cashflow = calculate_cashflow(prop["rent"], prop["expenses"], prop["loan"])

        roi = calculate_roi(cashflow * prop["years"], price)
        irr = calculate_irr(price, cashflow, prop["years"])

        return {
            "price": round(price,2),
            "roi": round(roi,2),
            "irr": round(irr,2)
        }

    return jsonify({
        "property1": analyze(data["property1"]),
        "property2": analyze(data["property2"])
    })


@app.route("/api/history", methods=["GET"])
@login_required
def api_history():
    analyses = Analysis.query.filter_by(user_id=current_user.id).all()

    data = []
    for a in analyses:
        data.append({
            "id": a.id,
            "roi": a.roi,
            "price": a.predicted_price,
            "risk": a.risk_level,
            "created_at": a.created_at
        })

    return jsonify(data)




@app.route("/api/delete-analysis/<int:id>", methods=["DELETE"])
@login_required
def api_delete_analysis(id):
    analysis = Analysis.query.get(id)

    if not analysis or analysis.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(analysis)
    db.session.commit()

    return jsonify({"message": "Deleted successfully"})

@app.route("/api/trends", methods=["GET"])
@login_required
def api_trends():

    # OPTIONAL: restrict to normal users only
    if current_user.role == "admin":
        return jsonify({"error": "Not allowed"}), 403

    analyses = Analysis.query.filter_by(user_id=current_user.id)\
                .order_by(Analysis.created_at).all()

    dates = []
    prices = []
    rois = []

    for a in analyses:
        dates.append(a.created_at.strftime("%Y-%m-%d"))
        prices.append(a.predicted_price)
        rois.append(a.roi)

    return jsonify({
        "dates": dates,
        "prices": prices,
        "rois": rois
    })


@app.route("/api/admin/stats", methods=["GET"])
@login_required
def api_admin_stats():
    if current_user.role != "admin":
        return jsonify({"error": "Access denied"}), 403

    total_users = User.query.count()
    total_analysis = Analysis.query.count()

    return jsonify({
        "total_users": total_users,
        "total_analysis": total_analysis
    })
# =========================
# CHATBOT
# =========================
@app.route("/chat", methods=["POST"])

def chat():
    try:
        user_msg = request.json.get("message")

        response = client.chat.completions.create(
           model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful real estate investment assistant."},
                {"role": "user", "content": user_msg}
            ]
        )

        reply = response.choices[0].message.content

        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=False, port=5001)