#!/bin/bash

export FLASK_APP=app.py;
export FLASK_ENV=production;
flask run -h 0.0.0.0;