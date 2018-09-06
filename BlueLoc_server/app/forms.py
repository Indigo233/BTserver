# -*- coding:utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from  app import app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/wangweiguo/repos/BlueLoc_server/app/db/blueloc.db?check_same_thread=False'
db = SQLAlchemy(app)

class Building(db.Model):
    __tablename__ = "Building"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), index=True, nullable=False)
    loc = db.Column(db.String(200), nullable=True)
    def __repr__(self):
        return '<building %r>' % self.name


class Floor(db.Model):
    __tablename__ = "Floor"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    floor_num = db.Column(db.Integer, index=True, nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('Building.id'), nullable=False)
    building = db.relationship('Building',
                               backref=db.backref('floors', lazy=True))

    def __repr__(self):
        return '(floor %r, x %r, y %r)' % (self.floor_num, self.x, self.y)



class Ibeacon(db.Model):
    __tablename__ = 'Ibeacon'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    mac = db.Column(db.String(30), index=True, nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    txpower= db.Column(db.Float, nullable=False)
    n = db.Column(db.Float, nullable=False)

    floor_id = db.Column(db.Integer, db.ForeignKey('Floor.id'), nullable=False)
    floor = db.relationship('Floor',
                               backref=db.backref('ibeacons', lazy=True))
    def __repr__(self):
        return '(ibeacon %r, x %r, y %r, height %r, txpower %r, n %r, floor %r)' % (self.mac, self.x, self.y, self.height, self.txpower, self.n, self.floor.floor_num)








