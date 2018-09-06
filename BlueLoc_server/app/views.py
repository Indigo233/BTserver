# -*- coding:utf-8 -*-
#!/usr/bin/env python
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from forms import db, Building, Floor, Ibeacon

import json
from flask import render_template, request
from app import app
from triangulation import Triangulation
measure = Triangulation('./app/coordination')
import traceback
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/getloc/', methods=['POST', 'GET'])
def getloc(jsonstring=None):
    data = json.loads(request.get_data().decode('utf-8'))	
    print("receive data: ", data)
    response = measure.getCoord(data, need_meta=True)
    print("response:", response)
    #rep = json.loads(response)
    #measure.mycnt += 1
    #rep["cnt"] = measure.mycnt
    #response = json.dumps(rep)
    return response

@app.route('/floor/', methods=['POST'])
def maintain_floor(jsonstring=None):

    data = json.loads(request.get_data())
    print(data)
    ret = {"success": 1}

    op = None
    floor_num = None
    try:
        op = data["op"]
        if op not in ["del", "add", "show"]:
            ret["success"] = 0
            ret["msg"] = "ERROR: invalid operation"
            return json.dumps(ret)

        if op in ["del", "add"]:
            if "floor_num" not in data:
                ret["success"] = 0
                ret["msg"] = "ERROR: please specify floor_num"
                return json.dumps(ret)
            floor_num = int(data["floor_num"])
        print("*******!!!********")
    except:
        ret["success"] = 0
        ret["msg"] = "ERROR: please specify opeartion"
        return json.dumps(ret)


    if op == "del":
        floors = Floor.query.filter_by(floor_num=floor_num).all()
        if len(floors) == 0:
            ret["success"] = 0
            ret["msg"] = "WARNING: the floor %r you try to del is not exist" % floor_num
            return json.dumps(ret)

        try:
            for floor in floors:
                db.session.delete(floor)
                db.session.commit()
            ret["msg"] = "SUCCESS: delete floor success"
            return json.dumps(ret)

        except:
            db.session.rollback()
            ret["success"] = 0
            ret["msg"] = "ERRROR: datebase inner error"
            return json.dumps(ret)

    elif op == "add":
        print("******@@@*****")
        try:
            #exist_floor = Floor.filter_by(floor_num=floor_num).all()
            #print(exist_floor)
            exist = Floor.query.filter_by(floor_num=floor_num).count() > 0
            if exist:
                ret["success"] = 0
                ret["msg"] = "ERROR: the floor is exist"
                return json.dumps(ret)

            x = float(data["x"])
            y = float(data["y"])

            building_name = "#1"  # 暂时就一栋楼 直接指定
            building = Building.query.filter_by(name=building_name).first()

            floor = Floor(floor_num=floor_num,x=x, y=y, building=building)
            db.session.add(floor)
            db.session.commit()
            ret["msg"] = "SUCCESS: add floor success"
            return json.dumps(ret)
        except :
            db.session.rollback()
            ret["success"] = 0
            ret["msg"] = "ERROR: add floor fail"
            return json.dumps(ret)

    elif op == "show":
        try:
            floors = Floor.query.all()
            resp = []
            for floor in floors:
                resp.append(floor.__repr__())
            ret["res"] = resp
            return json.dumps(ret)
        except Exception as e:
            traceback.print_exc()
            ret["success"] = 0
            ret["msg"] = "ERROR: database inner error"
            return json.dumps(ret)



@app.route('/ibeacon/', methods=['POST'])
def maintain_ibeacon(jsonstring=None):
    data = json.loads(request.get_data())

    ret = {"success": 1}

    op = None
    mac = None
    try:

        op = data["op"]
        if op not in ["del", "add", "show"]:
            ret["success"] = 0
            ret["msg"] = "ERROR: invalid operation"
            return json.dumps(ret)

        if op in ["del", "add"]:

            print("****?***")
            mac = data["mac"]
    except:
        ret["success"] = 0
        ret["msg"] = "ERROR: please specify same params"
        return json.dumps(ret)
    print("****??***")
    if op == "del":
        ibeacons = Ibeacon.query.filter_by(mac=mac).all()
        if len(ibeacons) == 0:
            ret["success"] = 0
            ret["msg"] = "WARNING: the ibeacon %r you try to del is not exist" % mac
            return json.dumps(ret)

        try:
            for ibeacon in  ibeacons:
                db.session.delete(ibeacon)
                db.session.commit()
            ret["msg"] = "SUCCESS: delete ibeacon success"
            return json.dumps(ret)
        except:
            db.session.rollback()
            ret["success"] = 0
            ret["msg"] = "ERRROR: datebase inner error"
            return json.dumps(ret)

    elif op == "add":
        try:
            exist = Ibeacon.query.filter_by(mac=mac).count() > 0
            if exist:
                ret["success"] = 0
                ret["msg"] = "ERROR: the ibeacon is exist"
                return json.dumps(ret)

            x = float(data["x"])
            y = float(data["y"])
            floor_num = int(data["floor_num"])
            floor = Floor.query.filter_by(floor_num=floor_num).first()
            height = float(data["height"])
            txpower = float(data["txpower"])
            n = float(data["n"])

            ibeacon = Ibeacon(mac=mac, x=x, y=y, height=height, txpower=txpower, n=n, floor=floor)
            db.session.add(ibeacon)
            db.session.commit()
            return json.dumps(ret)
        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            ret["success"] = 0
            ret["msg"] = "ERROR: add ibeacon fail"
            return json.dumps(ret)
    elif op == "show":
        if "floor_num" in data:
            floor_num = data["floor_num"]
            floor = Floor.query.filter_by(floor_num=floor_num).first()
            if not floor:
                ret["success"] = 0
                ret["msg"] = "ERROR: floor %r is not exist" % floor_num 
                return json.dumps(ret)
            ibeacons = floor.ibeacons
        else:
            ibeacons = Ibeacon.query.all()

        resp = []
        for i in ibeacons:
            resp.append(i.__repr__())
        ret["res"] = resp
        return json.dumps(ret)

