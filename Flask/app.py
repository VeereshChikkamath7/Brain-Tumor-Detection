from flask import Flask, request, jsonify, render_template, Response
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os
import numpy as np
from PIL import Image  


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registerpage')
def registerpage():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    required_fields = ['fullName', 'email', 'password', 'confirmPassword', 'phoneNumber', 'dob', 'gender', 'address']

    for field in required_fields:
        if not data.get(field):
            return jsonify({'status': 'fail', 'message': f'Missing field: {field}'}), 400

    if data['password'] != data['confirmPassword']:
        return jsonify({'status': 'Passwords are not Matching', 'message': 'Passwords do not match'}), 400

    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, data['email']):
        return jsonify({'status': 'Enter valid Email', 'message': 'Invalid email format'}), 400

    if not re.fullmatch(r'\d{10}', data['phoneNumber']):
        return jsonify({'status': 'Enter valid Phone number', 'message': 'Phone number must be 10 digits'}), 400

    try:
        datetime.strptime(data['dob'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'status': 'Enter valid Date of Birth', 'message': 'Invalid date format (use YYYY-MM-DD)'}), 400


    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="braintumor",
            charset='utf8'  
        )
        if conn.is_connected():
            print("✅ Database connection successful")
            cursor = conn.cursor()

            cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY,full_name VARCHAR(100),email VARCHAR(100) UNIQUE,password VARCHAR(100),confirm_password VARCHAR(100),phone_number VARCHAR(15),dob DATE,gender VARCHAR(10),address TEXT)""")
            print("✅ Table check/creation done")

            cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
            if cursor.fetchone():
                return jsonify({'status': 'User already exists', 'message': 'User with this email already exists'}), 409

            cursor.execute("""INSERT INTO users (full_name, email, password, confirm_password, phone_number, dob, gender, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (data['fullName'],data['email'],data['password'],data['confirmPassword'],data['phoneNumber'],data['dob'],data['gender'],data['address']))

            conn.commit()
            return jsonify({'status': 'Account Created Successfully'})
        else:
            print("❌ Database connection failed")
            return jsonify({'status': 'fail with success', 'message': 'Database connection failed'}), 500
    except Error as e:
        print(f"❌ Error: {e}")
        return jsonify({'status': 'fail with success', 'error': str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()





@app.route('/login', methods=['POST'])
def loginpage():
    data = request.get_json()

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="braintumor",
            charset='utf8'  
        )

        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE email = %s", (data['email'],))
            result = cursor.fetchone()

            if result:
                if result[0] == data['password']:
                    cursor.execute("""CREATE TABLE IF NOT EXISTS logtable (id INT AUTO_INCREMENT PRIMARY KEY,email VARCHAR(100),password VARCHAR(100))""")
                    print("✅ Login Table check/creation done")

                    cursor.execute("""INSERT INTO logtable (email, password) VALUES (%s, %s)""", (data['email'],data['password']))

                    conn.commit()
                    return jsonify({'status': 'Login successful'})
                else:
                    return jsonify({'status': 'Incorrect password'}), 401
            else:
                return jsonify({'status': 'Email not found'}), 404
        else:
            return jsonify({'status': 'DB connection failed'}), 500

    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500





brain_mri_model = load_model("brain_mri_filter_cnn_grayscale.h5")
tumor_classification_model = load_model("brain_tumor_detection_model.h5")


IMG_WIDTH, IMG_HEIGHT = 150, 150 
TUMOR_IMG_WIDTH, TUMOR_IMG_HEIGHT = 150, 150  



import google.generativeai as genai

genai.configure(api_key="AIzaSyDd4Fz2iQi4B0kF3Qu41JcHIc9Vcduy05k")  

def get_suggestions_from_gemini(tumor_type):
    prompt = f"Give medical suggestions, lifestyle tips, and next steps for a patient diagnosed with {tumor_type} brain tumor. Be gentle, helpful, and friendly."
    try:
        
        model = genai.GenerativeModel('gemini-1.5-flash')


        response = model.generate_content(prompt)


        return response.text if hasattr(response, 'text') else "No suggestions received."
    except Exception as e:
        print(f"Error while fetching from Gemini: {e}")
        return "Sorry, unable to fetch suggestions at the moment."

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"})
    
    try:

        filepath = os.path.join('uploads', file.filename)
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        file.save(filepath)
        

        image = Image.open(filepath).convert('L')  
        image = image.resize((IMG_WIDTH, IMG_HEIGHT))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=-1)
        image_array = np.expand_dims(image_array, axis=0)
        

        brain_mri_prediction = brain_mri_model.predict(image_array)[0][0]

        if brain_mri_prediction > 0.5:
            os.remove(filepath)
            return jsonify({
                "prediction": "❌ Not a Brain MRI Scan Image",
                "confidence": float(brain_mri_prediction)
            })
        
        image = Image.open(filepath).convert('RGB')  
        image = image.resize((TUMOR_IMG_WIDTH, TUMOR_IMG_HEIGHT))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        
        tumor_prediction = tumor_classification_model.predict(image_array)[0] 
        categories = ["glioma", "meningioma", "notumor", "pituitary"]
        tumor_result = categories[np.argmax(tumor_prediction)]
        confidence = float(np.max(tumor_prediction))  

        os.remove(filepath)

        suggestions = ""
        if tumor_result != "notumor":
            suggestions = get_suggestions_from_gemini(tumor_result)

        return jsonify({
            "prediction": "✅ Brain MRI Scan Image",
            "tumor_type": tumor_result,
            "confidence": confidence,
            "suggestions": suggestions
        })

    

    
    except Exception as e:
        return jsonify({"error": str(e)})



if __name__ == '__main__':
    app.run(debug=True)


