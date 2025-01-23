import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    TESSERACT_CONFIG = '--oem 3'
    OSRM_ENDPOINT = 'http://router.project-osrm.org/route/v1/driving'
    NOMINATIM_ENDPOINT = 'https://nominatim.openstreetmap.org/search'