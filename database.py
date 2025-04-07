import firebase_admin
from firebase_admin import credentials, db

cred_obj = credentials.Certificate("service-account-key.json")

databaseURL = "https://your-database-name.firebaseio.com"

default_app = firebase_admin.initialize_app(cred_obj, {"databaseURL": databaseURL})


cursor = db.reference("/tickets")
