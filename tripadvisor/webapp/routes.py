

import os.path
import json
from flask import Flask,url_for,request,render_template
from app import app

DataFolder = "../data"

@app.route('/')
def summary():
    summaryfile = "../summary.json"
    with open(summaryfile,"rt") as inputf:
        summaries = json.load(inputf)

    # sort hotels by its number of reviews
    summaries.sort(key = lambda s: -s["NumReviews"])

    # render the template and return the view
    return render_template("summary.html",summaries = summaries)
