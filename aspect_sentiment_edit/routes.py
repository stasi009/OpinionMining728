
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
    return render_template("index.html")

@app.route('/randomreview')
def next_random_review():
    review_id = app.mongoproxy.next_random_review_id()
    return redirect(url_for("show_review",review_id = review_id))

@app.route('/review/<review_id>',methods=['GET', 'POST'])
def show_review(review_id):
    if request.method == 'GET':
        review = app.mongoproxy.find_review_by_id(review_id)
        return render_template("review.html",review = review,aspect_options = AspectOptions,sentiment_options = SentimentOptions)
    elif request.method == 'POST':
        print "========================= in POST review ============="
        print "review_id: {}".format(review_id)
        return "<h2>testing POST</h2>"
    else:
        return "<h2>invalid request</h2>"
