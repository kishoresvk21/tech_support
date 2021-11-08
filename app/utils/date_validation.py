import datetime
from flask import jsonify
def validate(date_text):
    try:
        x=datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return x
    except ValueError:
        return jsonify(status=200,message="Incorrect data format, should be YYYY-MM-DD")