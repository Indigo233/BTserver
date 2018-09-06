#!/usr/bin/env python
import os, sys, json
from flask import render_template, flash, redirect, request, url_for, send_from_directory
from app import app
import json
from pattern_match import PatternMatch


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

p = PatternMatch('./app/FingerprintDatabase.csv')
print p.names
@app.route('/getloc/<jsonstring>')
@app.route('/getloc/', methods=['POST', 'GET'])
def getloc(jsonstring=None):
    data = json.loads(request.get_data())
    print data
    #data = data[0]
    #content = json.loads(data['content'])
    print data, type(data)
    for k in data:
	print k
	print data[k]
    print data
    pattern = []
    for name in p.names:
        if name in data:
	    pattern.append(float(data[name]) )
        else:
            pattern.append(-100)	
    print pattern
    coord = p.getMatchCoord(pattern)
    return json.dumps(coord) 

