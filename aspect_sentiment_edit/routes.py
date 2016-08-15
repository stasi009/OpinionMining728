
import json
from flask import Flask,url_for,request,render_template,redirect
from app import app
from review import Review,ReviewsDal

@app.route('/')
def home():
    return redirect(url_for('next_random_review'))

@app.route('/randomreview')
def next_random_review():
    review = app.mongoproxy.next_random_review()
    return render_template("review.html",review = review)
