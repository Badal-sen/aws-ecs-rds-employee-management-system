from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Version 2 - Deployed from Github"