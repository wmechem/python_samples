# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 10:56:07 2016

@author: will

Make sure ./DATA and ./UPLOADS directories exist and permissions are set

Module provides supporting functions for endpoints created in acme.py
pylint (8.45/10 - too many local variables in process_work_file) 2016/05/14 
flake8 (visual indent messages, unused 'headers' var) 2016/05/14

"""
import csv

import sqlite3

import json

from validate import validate_order

# path to SQLite database. Make sure directory exists and permissions are set
PATH_TO_DB = './DATA/orders.db'


class WorkFileError(Exception):
    """ Subclass Exception for work file import error """
    pass


class ProcessWorkFileError(Exception):
    """ Subclass Exception for work file process error """
    pass


class ValidateOrderError(Exception):
    """ Subclass Exception for order validate error """
    pass


class DatabaseOperationError(sqlite3.OperationalError):
    """ Subclass Exception for SQL create / alter table error """
    pass


def import_file(work_file):
    """ Import csv file.  Set up database if needed """

    try:

        columns = get_headers(work_file)
        results_create_table_query = create_table_query(columns)
        results_create_table_not_exists = create_table_not_exists(
            results_create_table_query)
        results_add_columns_not_exists = add_column_not_exists(columns)
        results_process = process_work_file(work_file, columns)
        results = {'Import Results': [{'work_file': work_file,
                 'header_row': columns,
                 'create_table_query': results_create_table_query,
                 'create_table_if_not_exists': results_create_table_not_exists,
                 'add_columns_not_exists': results_add_columns_not_exists,
                 'process': results_process}]
                 }
        results = str(results)
        return results

    except WorkFileError:
        raise WorkFileError("Error importing file: %s" % str(work_file))


def get_headers(work_file):
    """ Get csv file headers to use for db columns """

    with open(work_file) as work_file:
        reader = csv.reader(work_file, delimiter='|')
        headers = reader.next()
        headers.append('valid_flag')
        headers.append('validation_errors')

    return headers


def process_work_file(work_file, columns):
    """ read csv file rows and process each according to rule
    7 then validate other rules by passing to validate.validateOrder.
    """
    try:

        with open(work_file) as work_file:
            reader = csv.reader(work_file, delimiter='|')
            headers = reader.next()  # skip headers
            first_row = reader.next()

            previous_row = first_row
            previous_row.append('false')
            previous_row.append('not validated')
            row_counter = 0  # row counter
            for row in reader:
                row_counter += 1
                row.append('false')
                row.append('not validated')

                (order_id, name, email, state, zipcode, birthday,
                    valid_flag, validation_errors) = row

                (pr_order_id, pr_name, pr_email,
                    pr_state, pr_zipcode,
                    pr_birthday, pr_valid_flag,
                    pr_validation_errors) = previous_row

                if state == pr_state and zipcode == pr_zipcode:
                    #passes rule 7
                    valid_row = (order_id, name, email,
                                state, zipcode, birthday,
                                "true", "passed rule 7")

                    results = save_to_db(columns, valid_row)
                    previous_row = row

                else:

                    print "Validating order_id %s row %s " % (str(order_id),
                     str(row_counter))
                    validated_row = validate_order(row)

                    print "Validated "
                    print validated_row
                    results = save_to_db(columns, validated_row)
                    previous_row = row

        results = "Imported and validated %s" % str(work_file)

        return results

    except ProcessWorkFileError as process_error:
        return "Error processing work file %s " % str(process_error)


def create_table_query(columns):
    """ Construct query to create table in db """

    query = 'CREATE TABLE IF NOT EXISTS ORDERS ('

    for col in columns:
        query += col
        query += ' TEXT,'
    query = query.rstrip(",")
    query += ')'

    return query


def create_table_not_exists(create_table_sql):
    """ Execute create_table_query """
    conn = sqlite3.connect(PATH_TO_DB)

    cur = conn.cursor()
    try:
        cur.execute(create_table_sql)

    except DatabaseOperationError as create_table_error:
        conn.close()
        return "Error creating ORDERS TABLE %s" % str(create_table_error)

    conn.close()

    return 'success'


def add_column_not_exists(columns):
    """ Add additional columns to db table if new columns are
    added with new file import.
    """
    conn = sqlite3.connect(PATH_TO_DB)

    cur = conn.cursor()
    for column in columns:
        print column
        try:
            cur.execute("ALTER TABLE ORDERS ADD COLUMN '%s' 'TEXT'" % column)

        except Exception as error:
            if str(error).find('duplicate column name') != -1:
                pass
            else:
                raise Exception(str(error))

    conn.close()

    return 'success'


def save_to_db(columns, row):
    """ Write row to the db """
    try:
        conn = sqlite3.connect(PATH_TO_DB)

        cur = conn.cursor()

        keys = ','.join(columns)
        question_marks = ','.join(list('?'*len(row)))
        values = tuple(row)
        results = cur.execute('INSERT INTO ORDERS ('
            + keys + ') VALUES (' + question_marks + ')', values)
        conn.commit()
        conn.close()

        return results

    except DatabaseOperationError as database_operation_error:
        return "Save to DB error %s" % str(database_operation_error)


def query_orders(valid_flag, limit, offset):
    """ Query db to list orders matching args. """
    print limit, offset, valid_flag

    if valid_flag == '1':
        valid_flag = 'true'
    else:
        valid_flag = 'false'

    conn = sqlite3.connect(PATH_TO_DB)

    cur = conn.cursor()

    query = "select id, name, valid_flag from orders where valid_flag = '%s' \
    limit %s offset %s" % (valid_flag, limit, offset)

    print query

    results = {}
    results['valid_flag_query'] = valid_flag

    cursor = cur.execute(query)

    results['results'] = []

    for row in cursor:
        item = {}
        order_id, name, valid_flag = row
        item['order_id'] = order_id
        item['name'] = name
        item['valid'] = valid_flag
        results['results'].append(item)

    conn.close()

    results = json.dumps(results)

    return results


def get_order_by_id(order_id):
    """ Query db to return a single record by order_id

        {"order_id": 2075,
        "name": "Vinton Cerf",
        "state": "NJ",
        "zipcode": 08999,
        "birthday": "June 23, 1943",
        "valid": false,
        "errors": [{"rule": "AllowedStates", "message": "We don't ship to NJ",
        "rule": "ZipCodeSum", "message": "Your zipcode sum is too large"}]}

    """

    conn = sqlite3.connect(PATH_TO_DB)

    cur = conn.cursor()

    query = "select id, name, state, zipcode, birthday, valid_flag, \
    validation_errors from orders where id = '%s'" % str(order_id)

    results = {}

    cursor = cur.execute(query)

    results['results'] = []

    for row in cursor:
        item = {}

        (order_id, name, state, zipcode, birthday,
            valid_flag, validation_errors) = row

        item['order_id'] = order_id
        item['name'] = name
        item['state'] = state
        item['zipcode'] = zipcode
        item['birthday'] = birthday
        item['valid'] = valid_flag
        item['validation_errors'] = validation_errors
        results['results'].append(item)

    conn.close()

    results = json.dumps(results)

    return results
