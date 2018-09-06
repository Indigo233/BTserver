#!/usr/bin/env python
from forms import *

import json
from flask import render_template, request
from app import app
from triangulation import Triangulation
measure = Triangulation('./app/coordination')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/getloc/', methods=['POST', 'GET'])
def getloc(jsonstring=None):
    data = json.loads(request.get_data())	
    print("receive data: ", data)
    response = measure.getCoord(data, need_meta=True)
    print("response:", response)
    #rep = json.loads(response)
    #measure.mycnt += 1
    #rep["cnt"] = measure.mycnt
    #response = json.dumps(rep)
    return response
