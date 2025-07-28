from firebase_admin import credentials
import firebase_admin
from dotenv import load_dotenv
import os
import json

load_dotenv()


key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
cred = credentials.Certificate(key_path)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ctu-moalbaolgs-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Update this to match your Firebase URL
})