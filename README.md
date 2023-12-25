# Thai ID Card OCR App

<img width="1440" alt="Screenshot 2023-12-25 at 11 14 26 PM" src="https://github.com/anmolgupta8/Thai-ID-OCR-App/assets/112186184/c84565fe-2999-4d3c-b9c1-9bcaff2e7560">


This Flask web application extracts information from Thai ID cards using Optical Character Recognition (OCR). Users can upload images of Thai ID cards, and the app extracts details such as identification number, name, last name, and date of birth. The information is stored in a SQLite database, and users can view, delete, and update the extracted data through the web interface.

## Setup Instructions

### Prerequisites

- Python 3
- Flask
- Pillow (PIL)
- pytesseract
- Tesseract OCR
- SQLite3

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/thai-id-ocr-app.git

2. **Navigate to the project directory:**
   ```bash
   cd thai-id-ocr-app

3. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv

    # On Windows
    venv\Scripts\activate
    
    # On macOS and Linux
    source venv/bin/activate

4. **Install required packages:**
   ```bash
   pip install -r requirements.txt

    # Install Tesseract OCR:
    # On Windows: Follow the instructions [here](link-to-instructions).
    # On macOS: brew install tesseract
    # On Linux (Ubuntu): sudo apt-get install tesseract-ocr


5. **Run the Flask application:**
   ```bash
   python app.py

You can get other required dependencies from requirements.txt

6. Open your web browser and navigate to http://127.0.0.1:5000/.
7. Follow the on-screen instructions to upload Thai ID card images, view extracted data, and perform delete and update operations.


## Architecture Overview

  Flask: Web framework used to create the application.
  
  SQLite: Lightweight database for storing user data.
  
  Tesseract OCR: Engine for recognizing text in images.
  
  Pillow (PIL): Python Imaging Library for image manipulation.



The application follows a client-server architecture, where Flask handles user requests, performs OCR using Tesseract, and stores/retrieves data from the SQLite database. The client-side is a simple HTML template allowing users to interact with the application through forms.

## Usage

  Upload: Select a Thai ID card image and click the "Upload" button.
  
  View Data: Extracted data is displayed in a table showing identification number, first name, last name, and date of birth.
  
  Delete: Click the "Delete" button to remove a record from the database.
  
  Update: Click the "Update" button, modify data in the form, and click "Update" to save changes.






    
