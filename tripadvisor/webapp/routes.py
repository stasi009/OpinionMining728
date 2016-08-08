

import os.path
import csv
from flask import Flask,url_for,request,render_template
from app import app

DataFolder = "../data"

@app.route('/')
def summary():
    summaryfile = os.path.join(DataFolder,"summary.csv")
    with open(summaryfile,"rt") as inputf:
        reader = csv.reader(inputf)
        summaries = [row for row in reader]

    # sort hotels by its number of reviews
    summaries.sort(key=lambda l: -int(l[-1]))# last element is number of reviews

    # render the template and return the view
    return render_template("summary.html",summaries = summaries)
