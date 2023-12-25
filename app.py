from flask import Flask, render_template, request, url_for, redirect
from PIL import Image
import pytesseract
import os
import re
from datetime import datetime
import subprocess
from flask_sqlalchemy import SQLAlchemy
import sqlite3

os.makedirs('uploads', exist_ok=True)

pattern_id_no = r'\b\d{1,2} \d{4} \d{5} \d{2} \d\b'
pattern_name = r'\bName\b\s*(\S.*)'
pattern_ln = r'\bLastname\b\s*(\S.*)'
pattern_dob = r'(\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\. \d{4})'
date_patterns = [
    r'(\d{1,2}[\xb0°]\s\w+\. 202\d)',  # Pattern for "24° Jul. 2020"
    r'(\d{1,2}[\xb0°]\s\w+\. \d{4})',  # Pattern for "25° Jun. 1996"
    r'(\d{1,2} \w+\. \d{4})',
]
pattern_year = r'(\d{4})'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

conn = sqlite3.connect('thai_id.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM user_data')
rows = cursor.fetchall()

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/')
def index():
    # Fetch data from the database
    conn = sqlite3.connect('thai_id.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_data')
    rows = cursor.fetchall()
    conn.close()

    # Pass data to the template
    result = {
        'text': {},  # You may need to update this if you have any specific data to display
        'data': rows,
    }

    return render_template('index.html', result=result)

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

    result = {
        'text' : text,
        'data' : rows,
    }

    print(result)

    # return render_template('index.html', result=result)
    return redirect(url_for('index'))

# ... (existing code)

def save_to_database(json_data):
# Connect to SQLite database (create a new one if it doesn't exist)
    conn = sqlite3.connect('thai_id.db')
    # Create a cursor object
    cursor = conn.cursor()

@app.route('/delete', methods=['POST'])
def delete():
    identification_number = request.form.get('identification_number')
    conn = sqlite3.connect('thai_id.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_data WHERE identification_number = ?', (identification_number,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update():
    identification_number = request.form.get('identification_number')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    date_of_birth = request.form.get('date_of_birth')

    conn = sqlite3.connect('thai_id.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE user_data 
        SET name = ?, last_name = ?, date_of_birth = ? 
        WHERE identification_number = ?
    ''', (first_name, last_name, date_of_birth, identification_number))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

def save_to_database(json_data):
# Connect to SQLite database (create a new one if it doesn't exist)
    conn = sqlite3.connect('thai_id.db')
    # Create a cursor object
    cursor = conn.cursor()
    # Create a table (if not exists)
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
            identification_number TEXT PRIMARY KEY,
            name TEXT,
            last_name TEXT,
            date_of_birth TEXT
        )
    ''')
    # Insert or replace into the user_data table
    cursor.execute('''
        INSERT OR REPLACE INTO user_data 
        (identification_number, name, last_name, date_of_birth) 
        VALUES (?, ?, ?, ?)
    ''', (json_data['identification_number'], json_data['name'], json_data['last_name'], json_data['date_of_birth']))
    ''', (
        json_data['identification_number'],
        json_data['name'],
        json_data['last_name'],
        json_data['date_of_birth']
    ))''', (json_data['identification_number'], json_data['name'], json_data['last_name'], json_data['date_of_birth'])
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

    temp1 = re.search(pattern_id_no, text)
    if(temp1) : 
        identification_no = temp1.group()
        identification_no = identification_no.replace('O', '0')
    else : identification_no = "Could Not Extract"
    temp2 = re.search(pattern_name, text, re.IGNORECASE)
    if temp2 :
        name = temp2.group(1).strip()
    else :
        name = "Could Not Extract"
    temp3 = re.search(pattern_ln, text, re.IGNORECASE)
    if temp3:
        last_name = temp3.group(1).strip()
    else :
        last_name = "Could Not Extract"
    temp4 = re.search(pattern_dob, text, re.IGNORECASE)
    if temp4 :
        dob = temp4.group(1)
        dob_fm = datetime.strptime(dob, '%d %b. %Y').strftime('%d/%m/%Y')
    else :
        dob_fm = "Could Not Extract"
        

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