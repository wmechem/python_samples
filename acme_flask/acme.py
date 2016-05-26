# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 10:07:05 2016
@author: will mechem

main module sets up Flask app and end points etc.

NOTE: Make sure ',/UPLOADS' exists

pylint 5/8/2016
flake8 5/8/2016
"""

import os
from flask import Flask, request  # , redirect, url_for, send_from_directory
from werkzeug import secure_filename
from datetime import datetime
# from dateutil.relativedelta import *
from slugify import slugify
# import csv
# import json

from process import import_file, query_orders, get_order_by_id

app = Flask(__name__)

UPLOAD_FOLDER = './UPLOADS'

ALLOWED_EXTENSIONS = set(['csv'])  # not allow other file types to be uploaded

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    '''mask directory to stop malware uploads to unsafe directories'''

    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_file():
    '''main function upload and import file'''

    time_stamp = str(datetime.now())[:19] + "_"
    time_stamp = slugify(unicode(time_stamp))
    if request.method == 'POST':
        file_ = request.files['file']
        if file_ and allowed_file(file_.filename):
            filename = time_stamp + secure_filename(file_.filename)
            file_.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            work_file = str(os.path.join(app.config['UPLOAD_FOLDER'],
                            filename))

            return import_file(work_file)  # returns results -> http request

    return '''
    <!doctype html>
    <title>Acme Wines</title>
    <h1>Import orders file</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>'''


def orders():
    '''list orders with options: valid, limit, offset.
    redirects to process.queryOrders
    '''

    valid_flag = str(request.args.get('valid', '0'))
    limit = str(request.args.get('limit', 1000))
    offset = str(request.args.get('offset', 0))

    results = query_orders(valid_flag=valid_flag, limit=limit, offset=offset)

    return results


def single_order(order_id=None):
    ''' returns a single order matching order_id

    {"order_id": 2075,
    "name": "Vinton Cerf",
    "state": "NJ",
    "zipcode": 08999,
    "birthday": "June 23, 1943",
    "valid": false,
    "errors": [{"rule": "AllowedStates", "message": "We don't ship to NJ",
         "rule": "ZipCodeSum", "message": "Your zipcode sum is too large"}]}

    '''

    if order_id is not None:
        results = get_order_by_id(order_id)

        return results

    else:
        results = "No order id specified"

    return results


@app.route('/')
def welcome():
    '''returns welcome '''

    return 'Welcome to Acme Wine!'


app.add_url_rule('/orders/import/',
                 view_func=upload_file,
                 methods=['GET', 'POST'])


app.add_url_rule('/orders/',
                 view_func=orders,
                 methods=['GET'])

app.add_url_rule('/orders/<order_id>/',
                 view_func=single_order,
                 methods=['GET'])


if __name__ == '__main__':
    app.debug = True
    app.run()
