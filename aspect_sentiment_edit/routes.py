
import json
from flask import Flask,url_for,request,render_template,redirect
from app import app
from review import Review,ReviewsDal
import common

AspectOptions = [   common.AspectOverall,\
                    common.AspectClean,\
                    common.AspectLocation,\
                    common.AspectRoom,\
                    common.AspectService,\
                    common.AspectValue,\
                    common.AsepctNothing,\
                    common.AspectBusiness,\
                    common.AspectUnknown]
SentimentOptions = [    common.SentimentPositive,\
                        common.SentimentNegative,\
                        common.SentimentNeutral,\
                        common.SentimentUnknown]

@app.route('/')
def home():
    return redirect(url_for('next_random_review'))

@app.route('/randomreview')
def next_random_review():
    review = app.mongoproxy.next_random_review()
    return render_template("review.html",review = review,aspect_options = AspectOptions,sentiment_options = SentimentOptions)
