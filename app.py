from flask import Flask, render_template, request
from PIL import Image
import pytesseract
import os
import re
from datetime import datetime
import subprocess
from flask_sqlalchemy import SQLAlchemy
import sqlite3

pattern_id_no = r'\b\d{1,2} \d{4} \d{5} \d{2} \d\b'
pattern_name = r'\bName\b\s*(\S.*)'
pattern_ln = r'\bLastname\b\s*(\S.*)'
pattern_dob = r'(\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\. \d{4})'
pattern_doi = r'(\d{1,2}\xb0 \w+\. \d{4})'
date_patterns = [
    r'(\d{1,2}[\xb0°]\s\w+\. 202\d)',  # Pattern for "24° Jul. 2020"
    r'(\d{1,2}[\xb0°]\s\w+\. \d{4})',  # Pattern for "25° Jun. 1996"
    r'(\d{1,2} \w+\. \d{4})',
]
pattern_year = r'(\d{4})'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template('index.html', error='No file provided')

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error='No selected file')

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Perform OCR
    text = perform_ocr(file_path)

    return render_template('index.html', result=text)

def save_to_database(json_data):
# Connect to SQLite database (create a new one if it doesn't exist)
    conn = sqlite3.connect('thai_id.db')
    # Create a cursor object
    cursor = conn.cursor()
    # Create a table (if not exists)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            identification_number TEXT PRIMARY KEY,
            name TEXT,
            last_name TEXT,
            date_of_birth TEXT
        )
    ''')
    cursor.execute('''
        INSERT OR REPLACE INTO user_data 
        (identification_number, name, last_name, date_of_birth) 
        VALUES (?, ?, ?, ?)
    ''', (json_data['identification_number'], json_data['name'], json_data['last_name'], json_data['date_of_birth']))
    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

def perform_ocr(file_path):
    # Set TESSDATA_PREFIX environment variable
    tesseract_cmd = ['tesseract', file_path, 'output_text.txt', '--psm', '6']
    subprocess.run(tesseract_cmd)
    os.environ['TESSDATA_PREFIX'] = r'/usr/local/share/tessdata'


    img = Image.open(file_path)
    text = pytesseract.image_to_string(img, lang='eng')

    print("Raw Tesseract Output:")
    print(text)

    identification_no = re.search(pattern_id_no, text).group()
    name = re.search(pattern_name, text, re.IGNORECASE).group(1).strip()
    last_name = re.search(pattern_ln, text, re.IGNORECASE).group(1).strip()
    dob = re.search(pattern_dob, text, re.IGNORECASE).group(1)
    dob_fm = datetime.strptime(dob, '%d %b. %Y').strftime('%d/%m/%Y')

    data = {
        "identification_number": identification_no,
        "name": name,
        "last_name": last_name,
        "date_of_birth": dob_fm,
    }
    print("Data to be saved to database:", data)
    # Save OCR result to the database
    save_to_database(data)
    return data

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
