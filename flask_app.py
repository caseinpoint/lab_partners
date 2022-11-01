from flask import Flask, request, render_template, redirect, session, flash

app = Flask(__name__)
app.secret_key = 'notreallyasecret'

@app.route('/')
def index():
    return render_template('index.html')

