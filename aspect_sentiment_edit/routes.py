
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
                    common.AspectNothing,\
                    common.AspectBusiness,\
                    common.AspectUnknown]
SentimentOptions = [    common.SentimentPositive,\
                        common.SentimentNegative,\
                        common.SentimentNeutral,\
                        common.SentimentUnknown]

@app.route('/')
def home():
    return render_template("index.html",dbname = app.mongoproxy.dbname)

@app.route('/randomreview')
def next_random_review():
    review_id = app.mongoproxy.next_random_review_id()
    return redirect(url_for("show_review",review_id = review_id))

@app.route('/review',methods=['GET', 'POST'])
def show_review():
    review_id = request.args.get("review_id")
    classify = request.args.get("classify")
    print "############ classify =".format(classify)

    if request.method == 'GET':
        review = app.mongoproxy.find_review_by_id(review_id)

        if app.classifier is not None:
            app.classifier.classify(review)

        return render_template("review.html",
                                review = review,
                                dbname = app.mongoproxy.dbname,
                                aspect_options = AspectOptions,
                                sentiment_options = SentimentOptions)
    elif request.method == 'POST':
        success = app.mongoproxy.update_review(review_id,request.form)
        if success:
            # if 'check_after_update' is on, then just reload current review again
            next_review_id = review_id if 'check_after_update' in request.form else app.mongoproxy.next_random_review_id()
            return redirect(url_for("show_review",review_id = next_review_id))
        else:
            return "<h2 color='red'>!!! Update Failed !!!</h2>"
    else:
        return "<h2>invalid request</h2>"
