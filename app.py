from flask import Flask, render_template, request
from PIL import Image
import pytesseract
import os
import re
from datetime import datetime
import subprocess

pattern_id_no = r'\b\d{1,2} \d{4} \d{5} \d{2} \d\b'
pattern_name = r'\bName\b\s*(\S.*)'
pattern_ln = r'\bLastname\b\s*(\S.*)'
# pattern_dob = r'\b(\d{1,2} \w+\. \d{4})'
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

# Set Tesseract OCR executable path
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
# pytesseract.pytesseract.lang = 'eng'

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

    # doi = re.search(pattern_doi, text, re.IGNORECASE).group(1)
#     doi = re.findall(pattern_doi, text)
#     years_ = re.findall(pattern_year, text)
#     years = years_[::-1]
#     print(years)
#     # return
#     y_e = years[0]
#     y_s=y_e
#     for i in range(len(years)):
#         if(i==0):
#             continue
#         if(years[i][:2]==y_e[:2]):
#             y_s=years[i]
#             break
#     year_e = 0
#     # dates = re.findall(date_patterns, text)
#     for pattern in date_patterns:
#         match = re.search(pattern, text)
#         if match:
#             date_of_issuing = match.group(1)
#             # Remove degree symbol and any additional symbols or spaces
#             day, month_str, year = re.match(r'(\d{1,2})[\xb0°]\s(\w+)\. (\d{4})', date_of_issuing).groups()
# # Convert month abbreviation to numeric month
#             month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
#             month_numeric = month_dict[month_str]
#             print(y_e, y_s)
#             year_e = int(year) + int(y_e) - int(y_s)
#             # Format the date as "dd/mm/yyyy"
#             formatted_date_of_issuing = f"{day}/{month_numeric}/{year}"
#             print("Found date of issuing:", formatted_date_of_issuing)
#             doi = formatted_date_of_issuing
#             doe = f"{day}/{month_numeric}/{year_e}"
#             break  # Stop searching after the first match
#         else:
#             print("Date of issuing not found")
#         # print(dates)
#         print(doi, doe)
        # print(text)
    data = {
        "identification_number": identification_no,
        "name": name,
        "last_name": last_name,
        "date-of-birth": dob_fm,
        # "date-of-issue": doi,
        # "date-of-expiry": doe
    }
    # doi_fm = datetime.strptime(doi, '%d %b. %Y').strftime('%d/%m/%Y')
    return data

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
