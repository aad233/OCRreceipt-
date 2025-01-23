import re

def extract_dutch_info(text):
    # Initialize the extracted information dictionary
    extracted_info = {'address': None, 'phone': None, 'date': None}
    
    # Define regex patterns for Dutch address, phone number, and date
    address_pattern = r'\b\d{4}\s?[A-Z0-9]{2}\b'
    phone_pattern = r'\b(\+31|0)[1-9]\d{1,8}\b'
    date_pattern = r'\b\d{1,2}-\d{1,2}-\d{4}\b'
    
    # Search for patterns in the text
    address_match = re.search(address_pattern, text)
    phone_match = re.search(phone_pattern, text)
    date_match = re.search(date_pattern, text)
    
    # Update the dictionary with found information
    if address_match:
        extracted_info['address'] = address_match.group()
    if phone_match:
        extracted_info['phone'] = phone_match.group()
    if date_match:
        extracted_info['date'] = date_match.group()
    
    return extracted_info
