Brain-Tumor-Detection-Using-MRI-Scan  
🧠 Brain Tumor Detection Using MRI Scan  
Welcome to the Brain Tumor Detection Using MRI Scan project! This repository contains a CNN-based dual-model system to detect and classify brain tumors from MRI images, along with a Flask-based web application to upload scans and display results in real time. 🧬

📑 Project Overview  
This project leverages deep learning to classify brain tumors into the following categories:

Glioma  
Meningioma  
Pituitary  
No Tumor  

Key Features  
Tumor Detection Pipeline: Two-stage CNN-based system for MRI validation and tumor classification.  
Smart Suggestions: Integrates Google Gemini AI to generate medical suggestions based on diagnosis.  
Interactive UI: Simple HTML/CSS-based interface for uploading scans and displaying predictions.  

📁 Folder Structure  
brain_mri_filter_cnn_grayscale.h5 - CNN model for MRI scan validation.  
brain_tumor_detection_model.h5 - CNN model for tumor classification.  
brain-tumor-detection-96-accuracy.ipynb - Jupyter notebook for training and evaluation.  
app.py - Flask application script.  
templates/ - HTML template files.  
static/ - Static assets (CSS, images, etc.).  
uploads/ - Temporary image storage folder.  

🛠️ Requirements  
To run this project, you'll need the following libraries:

Flask - Web framework to serve the application.  
TensorFlow/Keras - To load and run CNN models.  
Pillow - For image processing.  
NumPy - For array manipulation.  
mysql-connector-python - To manage user database.  
google-generativeai - To fetch suggestions from Gemini AI.  

Install the dependencies using:  

pip install -r requirements.txt  

Dataset  
Dataset Name: Figshare, SARTAJ Brain MRI Dataset  
Source: Kaggle  
