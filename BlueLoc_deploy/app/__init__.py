#!/usr/bin/env python
from flask import Flask

app = Flask(__name__, static_folder='', static_url_path='')
app.config.from_object('config')
from app import views
