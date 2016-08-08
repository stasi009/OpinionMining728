
import json
from flask import Flask,url_for,request,render_template
from app import app

import os,sys
sys.path.append(os.path.abspath(".."))
from entities import Hotel

@app.route('/')
def summary():
    summaryfile = "../summary.json"
    with open(summaryfile,"rt") as inputf:
        summaries = json.load(inputf)

    # sort hotels by its number of reviews
    summaries.sort(key = lambda s: -s["NumReviews"])

    # render the template and return the view
    return render_template("summary.html",summaries = summaries)

@app.route('/details/<hotelId>')
def details(hotelId):
    path = "../data/{}.json".format(hotelId)
    hotel = Hotel(path)
    return render_template("details.html",hotel=hotel)
