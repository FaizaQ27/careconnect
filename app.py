# Import necessary libraries
from flask import Flask, request, jsonify, session
import joblib
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import pandas as pd
from flask_cors import CORS
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt
from datetime import datetime

# MongoDB collection for predictions

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGO_DB_URL"))
db = client["careconnect"]
users_collection = db["users"]
predictions_collection = db["predictions"]

app = Flask(__name__)

# Enable CORS for all routes (Allow credentials for session)
CORS(app, supports_credentials=True)

app.secret_key = "careconnect"

# Load the trained model
model = joblib.load("disease_predictor_model.joblib")

# Load dataset (Ensure it has 'disease', 'doctor', 'cures', and 'risk level' columns)
data = pd.read_csv("dataset.csv")

# Preprocessing function
nltk.download("punkt")
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))


def tokenize(text):
    """Function to clean and tokenize the input text."""
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    tokens = word_tokenize(text.lower())  # Tokenize and convert to lowercase
    tokens = [word for word in tokens if word not in stop_words]  # Remove stopwords
    return " ".join(tokens)



@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:  # Check if user is logged in
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Get the symptoms from the POST request body
        data_received = request.get_json()
        symptoms = data_received.get("symptoms", "")

        if not symptoms:
            return jsonify({"error": "No symptoms provided"}), 400

        # Preprocess the symptoms text
        processed_symptoms = tokenize(symptoms)

        # Predict disease using the model
        prediction = model.predict([processed_symptoms])
        disease = prediction[0]

        # Fetch additional information from dataset
        disease_info = data[data["disease"] == disease]

        # Get doctor recommendation from dataset
        doctor_list = [doc.strip() for doc in disease_info["doctor"].dropna().tolist()] or ["No doctor information available"]

        # Fetch suggested doctors from MongoDB
        suggested_doctors = list(
            users_collection.find(
                {"user_type": "doctor", "specialist_category": {"$in": doctor_list}},
                {"_id": 0, "name": 1, "specialist_category": 1},
            )
        )

        # If no suggested doctors found in MongoDB, send a fallback message
        if not suggested_doctors:
            suggested_doctors = [{"name": "No suitable doctor found", "specialist_category": "N/A"}]

        # Get possible cures
        cure_list = disease_info["cures"].dropna().tolist() or ["No cure information available"]

        # Get risk levels
        risk_level_list = disease_info["risk level"].dropna().tolist() or ["No risk level information available"]

        # Timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Store the prediction result in the database
        prediction_data = {
            "symptoms": symptoms,
            "disease": disease,
            "doctor": doctor_list,
            "suggested_doctors": suggested_doctors,
            "cure": cure_list,
            "risk_levels": risk_level_list,
            "timestamp": timestamp
        }

        predictions_collection.insert_one(prediction_data)

        return jsonify(
            {
                "disease": disease,
                "doctor": doctor_list,
                "suggested_doctors": suggested_doctors,
                "cure": cure_list,
                "risk_levels": risk_level_list,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/store-prediction", methods=["POST"])
def store_prediction():
    if "user" not in session:  # Ensure the user is logged in
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    user_email = session["user"]["email"]
    
    prediction_data = {
        "user_email": user_email,
        "symptoms": data["symptoms"],
        "disease": data["disease"],
        "doctor": data["doctor"],
        "suggested_doctors": data["suggested_doctors"],
        "cure": data["cure"],
        "risk_level": data["risk_level"],
        "timestamp": datetime.now(),
    }
    
    try:
        db["predictions"].insert_one(prediction_data)
        return jsonify({"message": "Prediction data saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-predictions", methods=["GET"])
def get_predictions():
    if "user" not in session:  # Check if user is logged in
        return jsonify({"error": "Unauthorized"}), 401

    try:
        email = session["user"]["email"]

        # Fetch stored predictions from MongoDB for the logged-in user
        predictions = db["predictions"].find({"user_email": email})  # Assuming predictions are stored in "predictions" collection
        prediction_list = []

        for prediction in predictions:
            prediction_list.append({
                "symptoms": prediction["symptoms"],
                "disease": prediction["disease"],
                "doctor": prediction["doctor"],
                "cure": prediction["cure"],
                "risk_level": prediction["risk_level"],
                "timestamp": prediction["timestamp"]
            })

        return jsonify({"predictions": prediction_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Helper function to hash passwords
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


# Helper function to check password
def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


# Signup route
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    user_type = data.get("user_type")  # "patient" or "doctor"
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not email or not password or not name:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if the email already exists
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Email already in use"}), 400

    # Hash the password before storing
    hashed_password = hash_password(password)

    # Store user details in MongoDB
    user_data = {"name": name, "email": email, "password": hashed_password, "user_type": user_type}

    if user_type == "doctor":
        specialist_category = data.get("specialist_category")
        if not specialist_category:
            return jsonify({"error": "Specialist category is required for doctors"}), 400
        user_data["specialist_category"] = specialist_category

    users_collection.insert_one(user_data)
    return jsonify({"message": "Signup successful"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user_type = data.get("user_type")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = users_collection.find_one({"email": email, "user_type": user_type})
    
    if not user or not check_password(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 400

    session.permanent = True  # Ensure session is persistent
    session["user"] = {
        "email": user["email"],
        "name": user["name"],
        "user_type": user["user_type"]
    }

    return jsonify({"message": "Login successful", "user_type": user["user_type"]}), 200

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)  # Remove user session
    return jsonify({"message": "Logout successful"}), 200


@app.route("/profile", methods=["GET"])
def profile():
    if "user" not in session:  # Check session correctly
        return jsonify({"error": "Unauthorized"}), 401

    # Extract user email from session
    email = session["user"]["email"]
    
    # Fetch user details from the database
    user = users_collection.find_one({"email": email}, {"_id": 0, "password": 0})

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200

@app.route("/available-doctors", methods=["GET"])
def available_doctors():
    try:
        # Fetch all doctors from the database
        doctors = list(
            users_collection.find(
                {"user_type": "doctor"},  # Filter by user_type = doctor
                {"_id": 0, "name": 1, "specialist_category": 1},  # Only return name and specialist category
            )
        )

        # If no doctors found, send a fallback message
        if not doctors:
            return jsonify({"message": "No doctors available"}), 404

        return jsonify({"doctors": doctors}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
