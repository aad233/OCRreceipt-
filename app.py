from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pytesseract
import re
import phonenumbers
# Add this under your existing imports
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename
from pytesseract import TesseractNotFoundError

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Configure Tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def validate_phone_number(number):
    try:
        parsed = phonenumbers.parse(number, "NL")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, 
                phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except:
        return None
    return None

def parse_ocr_text(text):
    results = {
        'address': 'Not detected',
        'postal_code': 'Not detected',
        'city': 'Not detected',
        'phone': 'Not detected'
    }
    
    # Postal code and city detection
    postal_code_match = re.search(r'\b(\d{4}\s*[A-Za-z]{2})\b', text)
    if postal_code_match:
        results['postal_code'] = postal_code_match.group(1).strip()
        city_match = re.search(r'(?<=' + re.escape(results['postal_code']) + r')\s+([A-Za-z]+)', text)
        if city_match:
            results['city'] = city_match.group(1).strip()
    
    # Address detection
    address_match = re.search(r'(\b[A-Za-z]+\s+\d+\b)', text)
    if address_match:
        results['address'] = address_match.group(1).strip()
    
    # Phone number detection
    phone_match = re.search(r'(\+?[\d\s\-\(\)]{7,}\d)', text)
    if phone_match:
        validated_phone = validate_phone_number(phone_match.group(1).strip())
        if validated_phone:
            results['phone'] = validated_phone
    
    # City fallback check
    if results['city'] == 'Not detected' and 'Amsterdam' in text:
        results['city'] = 'Amsterdam'
    
    return results

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
            
        if not allowed_file(file.filename):
            flash('Invalid file type. Allowed formats: PNG, JPG, JPEG', 'error')
            return redirect(url_for('index'))
            
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        
        try:
            img = Image.open(save_path)
            text = pytesseract.image_to_string(img)
            
            parsed_data = parse_ocr_text(text)
            
            if not any(v != 'Not detected' for v in parsed_data.values()):
                flash('No structured data could be extracted', 'warning')
                
            return render_template('result.html', 
                                 text=text, 
                                 image_path=save_path,
                                 parsed_data=parsed_data)
            
        except UnidentifiedImageError:
            flash('Invalid image file', 'error')
        except TesseractNotFoundError:
            flash('OCR engine not configured properly', 'error')
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'error')
            
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File size exceeds 2MB limit', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)