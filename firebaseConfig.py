# firebase_config.py

import firebase_admin
from firebase_admin import credentials, firestore

# Only initialize Firebase once
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
