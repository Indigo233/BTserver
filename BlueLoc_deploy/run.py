#!/usr/bin/env python
from app import app
print(app)
app.debug = True
app.run(host='0.0.0.0')
