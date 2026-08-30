# Essentail Libraries for Ridex Application
from datetime import datetime, timezone
import os
import certifi
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ridex_super_secret_key_2026")

# MongoDB Database setup 
MONGO_URI = os.environ.get(
    "MONGO_URI", 
    "mongodb+srv://n12763144_db_user:eMQ7IyU0dbCXa8tc@ridex.wcwz91s.mongodb.net/ridex_db?appName=Ridex"
)

# Added this  to fix SSL handshake failure on EC2
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database()

users_col = db["users"]
rides_col = db["rides"]

# Indexes for quick query matching
users_col.create_index("email", unique=True)

# role based Authentication setup
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            flash("Access denied. Admin authorization required.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

#view or routes calls for differents pages

#main page
@app.route("/")
def index():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("admin_panel"))
        return redirect(url_for("my_rides"))
    return redirect(url_for("login"))

#for signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name").strip()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        role = request.form.get("role", "passenger") 

        if users_col.find_one({"email": email}):
            flash("Email already registered. Please log in.", "error")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)
        user_doc = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": role,
            "created_at": datetime.now(timezone.utc)
        }
        users_col.insert_one(user_doc)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


#login page setup

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        user = users_col.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["name"] = user["name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")

            if user["role"] == "admin":
                return redirect(url_for("admin_panel"))
            return redirect(url_for("my_rides"))
        
        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


#admin page routes
@app.route("/admin/approve/<ride_id>", methods=["POST"])
@admin_required
def approve_ride(ride_id):
    result = rides_col.update_one(
        {"_id": ObjectId(ride_id), "status": "Pending"},
        {"$set": {"status": "Approved"}}
    )
    if result.modified_count > 0:
        flash("Ride status updated to Approved!", "success")
    else:
        flash("Unable to approve ride or ride is not pending.", "error")
    return redirect(url_for("admin_panel"))


#login page routes
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


#implementation of the request a ride 
@app.route("/ride/new", methods=["GET", "POST"])
@login_required
def ride_request():
    if request.method == "POST":
        pickup = request.form.get("pickup_location").strip()
        dropoff = request.form.get("dropoff_location").strip()
        notes = request.form.get("notes", "").strip()

        ride_doc = {
            "passenger_id": ObjectId(session["user_id"]),
            "passenger_name": session["name"],
            "pickup_location": pickup,
            "dropoff_location": dropoff,
            "notes": notes,
            "status": "Pending",  # Pending, Confirmed, Completed, Cancelled
            "created_at": datetime.now(timezone.utc)
        }
        rides_col.insert_one(ride_doc)
        flash("Ride requested successfully!", "success")
        return redirect(url_for("my_rides"))

    return render_template("ride_request.html")


# routes for my rides
@app.route("/my-rides")
@login_required
def my_rides():
    user_id = ObjectId(session["user_id"])
    rides = list(rides_col.find({"passenger_id": user_id}).sort("created_at", -1))
    return render_template("my_rides.html", rides=rides)

#routes cancel a ride
@app.route("/ride/cancel/<ride_id>", methods=["POST"])
@login_required
def cancel_ride(ride_id):
    user_id = ObjectId(session["user_id"])
    result = rides_col.update_one(
        {"_id": ObjectId(ride_id), "passenger_id": user_id, "status": "Pending"},
        {"$set": {"status": "Cancelled"}}
    )
    if result.modified_count > 0:
        flash("Ride booking cancelled.", "success")
    else:
        flash("Cannot cancel ride or ride not found.", "error")
    return redirect(url_for("my_rides"))




# admin page calls
@app.route("/admin")
@admin_required
def admin_panel():
    rides = list(rides_col.find().sort("created_at", -1))
    return render_template("admin_panel.html", rides=rides)


# delete routes for admin
@app.route("/admin/delete/<ride_id>", methods=["POST"])
@admin_required
def delete_ride(ride_id):
    result = rides_col.delete_one({"_id": ObjectId(ride_id)})
    if result.deleted_count > 0:
        flash("Ride record deleted.", "success")
    else:
        flash("Record not found.", "error")
    return redirect(url_for("admin_panel"))


#runs the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)