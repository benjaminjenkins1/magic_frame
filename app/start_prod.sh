#!/bin/bash
source env/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=production
gunicorn -w 2 -b 127.0.0.1:8060 app:app
