"""
Created on Feb 21, 2013
@author: wmechem

This is the finRocket ALERT module.  It is code to monitor
incoming stories and process alerts based on settings saved by users.
Alerts may include ENTITIES, TICKERS, contained in the story title or
body as well as SENTIMENT etc.  See parse_rules()

Uses ZMQ to listen to incoming messages.

Alerts are sent via EMAIL or SMS based on user's preferences

pylint 7.5 / 10 2016/05/15 - needs refactoring



"""

from datetime import datetime
from email.mime.text import MIMEText
import simplejson as json
import logging
from multiprocessing import Process, Queue
import os
import re
import smtplib
import threading
import time

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import MySQLDB as mdb
from pandas import DataFrame
from pandas.io import sql
import zmq

#setup ZMQ
UA_CONTEXT = zmq.Context()
USER_ALERTS_PULL_ADDR = 'tcp://127.0.0.1:6040'

print "user_alerts module 2013_09_09_localIP"

HOME_DIR = os.environ['HOME']
print 'Home DIR is ', HOME_DIR

LOAD_ALERT_FREQ = 300  # seconds before checking for changes
DB_HOST = 'xxx5-22.compute-1.amazonaws.com'
ALERT_DB_LIMIT = 1000  # number of alerts to load
ALERT_DB_OFFSET = 0

logging.basicConfig(filename=HOME_DIR + "/kj_alerts.log", level=logging.DEBUG)

logging.info("Starting User Alerts Monitor @ " + str(datetime.now()))

MODULE_NAME = "User Alerts Monitor"

VERBOSE = 0  # set VERBOSE != 1 to turn off extra logging

APP = Flask(__name__)

DB = SQLAlchemy(APP)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://kj_user:pwd@' + (
    DB_HOST + '/kj_feb_2013_01')

USER_ALERTS = ""


class UserProfile(DB.Model):
    """ Access user profiles. """
    def __init__(self):
        pass

    __tablename__ = 'kj_users'
    id_ = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(80))
    userpasswd = DB.Column(DB.String(80))
    user_created_date = DB.Column(DB.Date)
    user_email = DB.Column(DB.String(100))
    user_mobile = DB.Column(DB.String(40))
    user_carrier = DB.Column(DB.String(40))


class UserAlert(DB.Model):
    """ Access user alerts. """
    __tablename__ = 'kj_user_alerts'
    id_ = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(80))
    user_alert_name = DB.Column(DB.String(20))
    user_alert_created_date = DB.Column(DB.Date)
    user_alert_scope = DB.Column(DB.String(80))
    user_alert_condition = DB.Column(DB.String(40))
    user_alert_keywords = DB.Column(DB.String(2000))
    user_alert_actions = DB.Column(DB.String(40))
    user_alert_triggered_state = DB.Column(DB.String(40))
    user_alert_triggered_time = DB.Column(DB.Date)
    user_alert_delet = DB.Column(DB.Integer(1))
    user_alert_ext_op = DB.Column(DB.String(10))
    user_alert_ext_scop = DB.Column(DB.String(80))
    user_alert_ext_conditio = DB.Column(DB.String(40))
    user_alert_ext_keywords = DB.Column(DB.String(2000))

    def __init__(self, id_, username, a_name, a_created_date, a_scope,
        a_condition, a_keywords, a_actions, a_state, a_state_time,
        a_delete, a_ext_op, a_ext_scope, a_ext_condition, a_ext_keywords):
        """ Initialize alert attributes. """
        self.id_ = id_
        self.username = username
        self.user_alert_name = a_name
        self.user_alert_created_date = a_created_date
        self.user_alert_scope = a_scope
        self.user_alert_condition = a_condition
        self.user_alert_keywords = a_keywords
        self.user_alert_actions = a_actions
        self.user_alert_triggered_state = a_state
        self.user_alert_triggered_time = a_state_time
        self.user_alert_delete = a_delete
        self.user_alert_ext_op = a_ext_op
        self.user_alert_ext_scope = a_ext_scope
        self.user_alert_ext_condition = a_ext_condition
        self.user_alert_ext_keywords = a_ext_keywords


def do_log(msg):
    """ Generic logging function. """
    print msg
    if VERBOSE == 1:
        l_string = (MODULE_NAME + " "
            + msg + " " + str(datetime.now()))
        logging.info(l_string)

    else:
        return

    return


def load_user_alerts_df():
    """ Load user alerts. """
    con = mdb.connect(DB_HOST, 'kj_user', 'xxx', 'kj_feb_2013_01')
    dataframe = sql.read_frame("SELECT * FROM kj_user_alerts;", con)
    con.close()
    return dataframe


def load_user_alerts_in_q(user_alerts_rules_q):
    """ Periodically load user alerts in to a queue
    so that we can detect changes.
    """

    while True:

        try:
            #  Keep getting queue until empty then replace with rules from db
            rules = user_alerts_rules_q.get_nowait()
            user_alerts_rules_q.put(rules)

        except Exception:
            # if queue is empty load alerts from database
            df = load_user_alerts_df()
            user_alerts_rules_q.put(df)
            time.sleep(LOAD_ALERT_FREQ)
    return


def load_once_user_alerts(limit, offset):
    """ init user alerts once from DB then from q """
    results = UserAlert.query.limit(limit).offset(offset).all()
    json_results = []
    for result in results:
        data = {"id_": result.id_,
               'username': result.username,
               'user_alert_name': result.user_alert_name,
               'user_alert_scope': result.user_alert_scope,
               'user_alert_condition': result.user_alert_condition,
               'user_alert_keywords': result.user_alert_keywords,
               'user_alert_actions': result.user_alert_actions,
               'user_alert_triggered_state': result.user_alert_triggered_state,
               'user_alert_triggered_time': result.user_alert_triggered_time,
               'user_alert_delete': result.user_alert_delete,
               'user_alert_ext_op': result.user_alert_ext_op,
               'user_alert_ext_scope': result.user_alert_ext_scope,
               'user_alert_ext_condition': result.user_alert_ext_condition,
               'user_alert_ext_keywords': result.user_alert_ext_keywords,
               }

        json_results.append(data)

    return json_results


def load_user_profile(username):
    """ get user info from DB """
    result = UserProfile.query.filter_by(username=username).first()
    json_result = {'username': result.username,
                   'userpasswd': result.userpasswd,
                   'user_created_date': result.user_created_date,
                   'user_email': result.user_email,
                   'user_mobile': result.user_mobile,
                   'user_carrier': result.user_carrier
                   }
    return json_result


def get_messages_from_kj_main_t(context, user_alerts_pull_addr,
        in_messages_pool_q):
    """ Listen for messages to parse coming from main process
    and put them in a queue.
    """
    context = context

    alerts_pull_socket = context.socket(zmq.PULL)
    alerts_pull_socket.connect(USER_ALERTS_PULL_ADDR)

    while True:
        if VERBOSE == 1:
            l_string = MODULE_NAME + " waiting for new message " + str(
                datetime.now())
            logging.info(l_string)

        message = alerts_pull_socket.recv_pyobj()

        if VERBOSE == 1:
            l_string = MODULE_NAME + ("putting message in in_messages_q " +
             str(datetime.now()))
            logging.info(l_string)

        in_messages_pool_q.put(message)
        time.sleep(.1)

    return


def send_alert(target, user_alert_name, alert_out_message):
    """main SMTP handler"""

    comma_space = ', '
    dist_list = [target]
    smtpuser = 'msgs@wjtglobal.com'  # for SMTP AUTH, set SMTP username here
    smtppass = 'xxx'  # for SMTP AUTH, set SMTP password here

    msg = MIMEText(alert_out_message)
    msg['Subject'] = user_alert_name
    msg['From'] = 'alerts@finrocket.com'
    msg['To'] = comma_space.join(dist_list)

    mailServer = smtplib.SMTP('smtp.1and1.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(smtpuser, smtppass)
    mailServer.sendmail(smtpuser, dist_list, msg.as_string())
    mailServer.close()

    return


def parse_rules(user_alerts_rules_q, new_rules_q):
    """ Get rules from q and parse them.  Create dictionary objects to
    quickly test for existence of a rule when messgaes come in.
    """

    sent_dict = {}
    sent_keys = [-2, -1.75, -1.5, -1.25, 0, 1.25, 1.5, 1.75, 2]
    for key in sent_keys:
        sent_dict[key] = []

    title_dict = {}
    title_not_dict = {}
    any_dict = {}
    any_not_dict = {}
    entities_dict = {}
    entities_not_dict = {}
    tickers_dict = {}
    tickers_not_dict = {}

    rules = user_alerts_rules_q.get()

    do_log("Got rules DF from user_alserts_rules_q" + str(rules))

    if VERBOSE == 1:
        l_string = MODULE_NAME + " loaded user alert rules " + (
            str(datetime.now()))

        logging.info(l_string)
    else:
        pass

    print rules

    for i, row in enumerate(rules.values):
        do_log("Row is " + str(i))
        do_log("Number of rules is " + str(len(rules.values)))

        id_, username, user_alert_name, user_alert_created_date, \
        user_alert_scope, user_alert_condition, user_alert_keywords, \
        user_alert_actions, user_alert_triggered_state, \
        user_alert_triggered_time, user_alert_delete, \
        user_alert_ext_op, user_alert_ext_scope, user_alert_ext_condition,\
        user_alert_ext_keywords = row

        print str(id_) + " " + user_alert_name + (
            " " + user_alert_scope + " " +
            user_alert_condition + " " + user_alert_keywords)

        user_alert_scope = user_alert_scope.upper()
        user_alert_condition = user_alert_condition.upper()
        rule_keywords = user_alert_keywords.split(' ')
        rule_keywords = set(rule_keywords)

        if user_alert_scope == 'TITLE' and (
            user_alert_condition == 'CONTAINS'):

            for key in rule_keywords:
                key = key.upper()

                if title_dict.get[key]:
                    title_dict[key].append(id_)
                else:
                    title_dict[key] = [id_]

        if user_alert_scope == 'TITLE' and (
            user_alert_condition == 'DOES NOT CONTAIN'):

            for key in rule_keywords:
                key = key.upper()

                if title_not_dict.get(key):
                    title_not_dict[key].append(id_)
                else:
                    title_not_dict[key] = [id_]

        if user_alert_scope == 'ANY' and (
            user_alert_condition == 'CONTAINS'):

            for key in rule_keywords:
                key = key.upper()

                if any_dict.get(key):
                    any_dict[key].append(id_)

                else:
                    any_dict[key] = [id_]

        if user_alert_scope == 'ANY' and (
            user_alert_condition == 'DOES NOT CONTAIN'):

            for key in rule_keywords:
                key = key.upper()

                if any_not_dict.get(key):
                    any_not_dict[key].append(id_)
                else:
                    any_not_dict[key] = [id_]

        if user_alert_scope == 'TICKER' and (
            user_alert_condition == 'CONTAINS'):

            for key in rule_keywords:
                key = key.upper()

                if tickers_dict.get(key):
                    tickers_dict[key].append(id_)
                else:
                    tickers_dict[key] = [id_]

        if user_alert_scope == 'TICKER' and (
            user_alert_condition == 'DOES NOT CONTAIN'):

            for key in rule_keywords:
                key = key.upper()

                if tickers_not_dict.get(key):
                    tickers_not_dict[key].append(id_)
                else:
                    tickers_not_dict[key] = [id_]

        if user_alert_scope == 'ENTITIES' and (
            user_alert_condition == 'CONTAINS'):

            for key in rule_keywords:
                key = key.upper()

                if entities_dict.get(key):
                    entities_dict[key].append(id_)
                else:
                    entities_dict[key] = [id_]

        if user_alert_scope == 'ENTITIES' and (
            user_alert_condition == 'DOES NOT CONTAIN'):

            for key in rule_keywords:
                key = key.upper()

                if entities_not_dict.get(key):
                    entities_not_dict[key].append(id_)
                else:
                    entities_not_dict[key] = [id_]

        if user_alert_scope == 'SENTIMENT':
            do_log("Processing SENTIMENT dictionary")

            do_log("Sentiment Alert processed for id_ " +
                str(id_) + " " + user_alert_scope + " " +
                    user_alert_condition + " " + str(user_alert_keywords))

            print user_alert_scope + " " + user_alert_condition

        if user_alert_scope == 'SENTIMENT' and user_alert_condition == '=':
            print user_alert_scope + " " + user_alert_condition

            user_alert_keywords = float(user_alert_keywords)

            for key in sent_dict.keys():

                if float(user_alert_keywords) == float(key):
                    print "Matched =", float(key), float(user_alert_keywords)
                    if sent_dict.get(key):
                        sent_dict[key].append(str(id_))

                        print sent_dict[key]
                        print str(id_) + (
                            "appending sent_dict for key " + str(key))
                    else:
                        #sent_dict[key = ser_alert_name
                        sent_dict[key] = [str(id_)]
                        print sent_dict[key]
                        print str(id_) + (
                            "creating entry in sent_dict for key " + str(key))
                else:
                    pass

        if user_alert_scope == 'SENTIMENT' and user_alert_condition == '>':
            print user_alert_scope + " " + user_alert_condition
            print "Keyword " + user_alert_keywords

            user_alert_keywords = float(user_alert_keywords)

            for key in sent_dict.keys():
                print "Sentiment Key: " + str(key)

                if float(user_alert_keywords) < float(key):
                    print "Matched >", float(key), float(user_alert_keywords)
                    if sent_dict.get(key):
                        sent_dict[key].append(str(id_))
                        print sent_dict[key]
                        print str(id_) + (
                            "appending sent_dict for key " + str(key))
                    else:
                        #sent_dict[key = ser_alert_name
                        sent_dict[key] = [str(id_)]
                        print sent_dict[key]
                        print str(id_) + (
                            "creating entry in sent_dict for key " + str(key))
                else:
                    pass

        if user_alert_scope == 'SENTIMENT' and user_alert_condition == '<':
            print user_alert_scope + " " + user_alert_condition

            user_alert_keywords = float(user_alert_keywords)

            for key in sent_dict.keys():

                if float(user_alert_keywords) > float(key):
                    print "Matched < ", float(key), float(user_alert_keywords)
                    if sent_dict.get(key):
                        sent_dict[key].append(str(id_))
                        print sent_dict[key]
                        print str(id_) + "appending sent_dict for key " + (
                            str(key))
                    else:
                        sent_dict[key] = str(id_)
                        print sent_dict[key]
                        print str(id_) + (
                            "creating entry in sent_dict for key " + str(key))
                else:
                    pass

        if user_alert_scope == 'SENTIMENT' and user_alert_condition == '=':
            print user_alert_scope + " " + user_alert_condition

            user_alert_keywords = float(user_alert_keywords)

            for key in sent_dict.keys():

                if float(user_alert_keywords) >= float(key):
                    print "Matched > ", float(key), float(user_alert_keywords)
                    if sent_dict.get(key):
                        sent_dict[key].append(str(id_))
                        print sent_dict[key]
                        print str(id_) + "appending sent_dict for key " + (
                            str(key))
                    else:
                        #sent_dict[key = user_alert_name
                        sent_dict[key] = [str(id_)]
                        print sent_dict[key]
                        print str(id_) + (
                            "creating entry in sent_dict for key " + str(key))
                else:
                    pass

        if user_alert_scope == 'SENTIMENT' and user_alert_condition == '=':
            print user_alert_scope + " " + user_alert_condition

            for key in sent_dict.keys():

                if float(user_alert_keywords) <= float(key):
                    print "Matched >", float(key), float(user_alert_keywords)
                    if sent_dict.get(key):
                        sent_dict[key].append(str(id_))
                        print sent_dict[key]
                        print str(id_) + " appending sent_dict for key " + (
                            str(key))
                    else:
                        sent_dict[key] = [str(id_)]
                        print sent_dict[key]
                        print str(id_) + (
                            "creating entry in sent_dict for key " + str(key))
                else:
                    pass

    print "Parsed all rules into dictionaries"
    print "Title Keys:" + str(title_dict.keys())
    print "Title Not Keys:" + str(title_not_dict.keys())
    print "Any Keys:" + str(any_dict.keys())
    print "Any Not Keys:" + str(any_not_dict.keys())
    print "Entities Keys:" + str(entities_dict.keys())
    print "Entities Not Keys:" + str(entities_not_dict.keys())
    print "Tickers Keys:" + str(tickers_dict.keys())
    print "Tickers Not Keys:" + str(tickers_not_dict.keys())

    if VERBOSE == 1:
        l_string = MODULE_NAME + " Parsed all rules into dictionaries " + (
            str(datetime.now()))
        logging.info(l_string)
    else:
        pass

    out_list = [rules, sent_dict, title_dict, any_dict,
              entities_dict, tickers_dict, any_not_dict,
              title_not_dict, entities_not_dict, tickers_not_dict]

    new_rules_q.put(out_list)

    return out_list


def get_new_rules(new_rules_q):
    """ Check queue for new rules. """

    print "Getting new rules"
    if VERBOSE == 1:
        l_string = MODULE_NAME + " Getting new rules " + (
            str(datetime.now()))
        logging.info(l_string)
    else:
        pass
    try:
        # get rules from queue if they exist
        new_rules = (rules, sent_dict, title_dict,
        any_dict, entities_dict, tickers_dict,
        any_not_dict, title_not_dict, entities_not_dict,
        tickers_not_dict) = new_rules_q.get_nowait()

    except Exception(Queue.Empty):
        print "No new rules to get"

    return new_rules


def get_new_message(in_messages_pool_q):
    """ Loop on message queue.get """

    while True:

        try:
                #see if we have a new message
                message = in_messages_pool_q.get()
                print "Message ", len(message)
                if VERBOSE == 1:
                    l_string = MODULE_NAME + "Message length " + (
                        str(len(message)) + " " + str(datetime.now()))
                    logging.info(l_string)
                else:
                    pass
                yield message
                pass

        except Queue.Empty:
            time.sleep(.1)
            pass


def parse_message(message):
    """ Parse fields from dict object received from main KJ process"""

    message = json.loads(message)
    m_title = message['m_title']
    m_description = message['m_description']
    m_sentiment = message['m_sentiment']
    m_tickers = message['m_tickers']
    m_entities = message['m_entities']
    m_link = message['m_link']

    alert_out_message = m_title[0:20]+" S"+m_sentiment+" "+m_link

    return (m_title, m_description, m_sentiment, m_tickers,
        m_entities, m_link), alert_out_message


def process_sent_dict(alert_dict, sent_dict, m_sentiment, alerts_fired):
    """ Check to see if sentiment alert is triggered. """

    alert_dict = sent_dict
    log_msg = "Processing " + str(alert_dict)
    do_log(log_msg)

    if m_sentiment:
        key = float(m_sentiment)
        alerts_fired.append(alert_dict[key])
        log_msg = "Alerts fired contains a sentiment alert " + (
            str(alerts_fired))
        do_log(log_msg)

    return alerts_fired


def get_any_tokens(m_title, m_description):
    """ Make tokens out of title and description text. """

    message = nltk.clean_html(m_description)
    log_msg = "Message len after m_description html clean:" + (
        str(len(message)))
    do_log(log_msg)

    if nltk.clean_html(m_title):
        m_title = nltk.clean_html(m_title)
        message = message + " " + m_title
        log_msg = "Message has length after title html clean:" + (
            str(len(message)))
        do_log(log_msg)

    else:
        log_msg = (
            "Error processing m_title with nltl.clean_html ")
        do_log(log_msg)

    message = nltk.word_tokenize(message)
    punctuation = re.compile(r'[-.?!,&":;()|0-9]')
    tokens = [punctuation.sub(" ", token) for token in message]
    log_msg = str(tokens)
    do_log(log_msg)

    return tokens


def process_any_dict(alert_dict, any_dict, m_title, m_description,
    alerts_fired):
    """ If title or description contain matching text alert is
    triggered.
    """

    log_msg = "Processing matches for ANY CONTAINS"
    do_log(log_msg)
    print log_msg

    alert_dict = any_dict
    log_msg = " processing " + str(alert_dict)
    do_log(log_msg)

    tokens = get_any_tokens(m_title, m_description)

    for token in set(tokens):
        token = token.upper()
        log_msg = "Looking for: " + token
        do_log(log_msg)

        if alert_dict.get(token):
            alerts_fired.append(alert_dict[token])
            log_msg = "Added " + str(alert_dict[token]) + (
                " to alerts_fired")
            do_log(log_msg)
        else:
            log_msg = "Token not found in alert_dict: " + token
            do_log(log_msg)

    return alerts_fired


def process_any_not_dict(alert_dict, any_not_dict, m_title, m_description,
     alerts_fired):
    """ If title or description contain matching (NOT) text alert
    is triggered.
    """

    log_msg = "Processing matches for ANY DOES NOT CONTAIN"
    do_log(log_msg)

    alert_dict = any_not_dict
    log_msg = "processing " + str(alert_dict)
    do_log(log_msg)

    tokens = get_any_tokens(m_title, m_description)

    count = 0
    for token in set(tokens):
        token = token.upper()
        log_msg = "Looking for: " + token
        do_log(log_msg)

        if alert_dict.get(token):
            count += 1
        else:
            pass

    if count == 0:
        for key in alert_dict.keys():
            alerts_fired.append(alert_dict[key])

    return alerts_fired


def get_title_tokens(m_title):
    """ Make tokens out of title text, """
    message = nltk.clean_html(m_title)
    message = nltk.word_tokenize(message)
    punctuation = re.compile(r'[-.?!,&":;()|0-9]')
    tokens = [punctuation.sub(" ", token) for token in message]

    return tokens


def process_title_dict(alert_dict, title_dict, m_title, alerts_fired):
    """ If title contains matching text alert is triggered. """

    log_msg = "Processing TITLE matches for CONTAINS"
    do_log(log_msg)

    alert_dict = title_dict
    log_msg = "processing " + str(alert_dict)
    do_log(log_msg)

    tokens = get_title_tokens(m_title)

    for token in tokens:
        token = token.upper()
        log_msg = "Looking for: " + token
        do_log(log_msg)
        if title_dict.get(token):
            alerts_fired.append(title_dict[token])
        else:
            pass

    return alerts_fired


def process_title_not_dict(alert_dict, title_not_dict, m_title, alerts_fired):
    """ If title does not contain matching text alert is triggered. """

    log_msg = "Processing TITLE matches for DOES NOT CONTAIN"
    do_log(log_msg)

    alert_dict = title_not_dict
    log_msg = "processing " + str(alert_dict)
    do_log(log_msg)

    tokens = get_title_tokens(m_title)

    count = 0
    for token in tokens:
        token = token.upper()
        log_msg = "Looking for: " + token
        do_log(log_msg)

        if alert_dict.get(token):
            count += 1
        else:
            pass
    if count == 0:
        for key in alert_dict.keys():
            alerts_fired.append(alert_dict[key])

    return alerts_fired


def process_tickers_dict(alert_dict, tickers_dict, m_tickers, alerts_fired):
    """ If tickers contains matching symbol alert is triggered. """

    log_msg = "Processing TICKERS matches for CONTAINS"
    do_log(log_msg)

    alert_dict = tickers_dict
    log_msg = "processing " + str(alert_dict)
    do_log(log_msg)

    for token in set(m_tickers.split(',')):
        token = token.upper()
        log_msg = "Looking for: " + token
        do_log(log_msg)

        if alert_dict.get(token):
            alerts_fired.append(alert_dict[token])
        else:
            pass

    return alerts_fired


def process_tickers_not_dict(alert_dict, tickers_not_dict, m_tickers,
     alerts_fired):
    """ If tickers does not contain matching symbol alert is triggered. """
    alert_dict = tickers_not_dict
    log_msg = "processing " + str(alert_dict)
    do_log(log_msg)

    log_msg = "Processing TICKERS matches for DOES NOT CONTAIN"
    do_log(log_msg)

    for token in set(m_tickers.split(',')):
        token = token.upper()
        log_msg = "Looking for: " + token
        do_log(log_msg)
        count = 0
        if alert_dict.get(token):
            count += 1
        else:
            pass
        if count == 0:
            for key in alert_dict.keys():
                alerts_fired.append(alert_dict[key])

    return alerts_fired


def process_entities_dict(alert_dict, entities_dict, m_entities, alerts_fired):
    """ If entities contains matching name alert is triggered. """

    log_msg = "Processing ENTITIES matches for CONTAINS"
    do_log(log_msg)

    alert_dict = entities_dict
    for token in set(m_entities.split(',')):
        token = token.upper()
        log_msg = "Looking for: " + token
        do_log(log_msg)
        if alert_dict.get(token):
            alerts_fired.append(alert_dict[token])
        else:
            pass

    return alerts_fired


def process_entities_not_dict(alert_dict, entities_not_dict, m_entities,
     alerts_fired):
    """ If entities does contain matching name alert is triggered. """

    alert_dict = entities_not_dict
    log_msg = "processing " + str(alert_dict)
    do_log(log_msg)

    log_msg = "Processing ENTITIES matches for DOES NOT CONTAIN"
    do_log(log_msg)

    count = 0
    for token in set(m_entities.split(',')):
        token = token.upper()
        log_msg = "Looking for: " + token
        do_log(log_msg)

        if alert_dict.get(message[token]):
            count += 1
        else:
            pass
    if count == 0:
        for key in alert_dict.keys():
            alerts_fired.append(entities_not_dict[key])

    return alerts_fired


def process_alerts_fired(alerts_fired, rules, alert_out_message):
    """ Process alerts_fired list.  """

    log_msg = "Beginning processing of alerts_fired" + (
                    str(alerts_fired))

    do_log(log_msg)

    alerts_list = []

    for id_ in alerts_fired:
        for i in id_:
            do_log("alerts_fired contains " + str(alerts_fired))

            do_log("alerts_fired id_[0] = " + str(i))

            alerts_list.append(i)
            do_log("Added " + str(i) + " to alerts_list -> " + (
                str(alerts_list)))

    alerts_list = set(alerts_list)

    do_log("alerts_list contains: " + str(alerts_list))
    print "alerts_list is:" + str(alerts_list)

    try:
        for alert_ in alerts_list:

            do_log("Alert is type " + str(type(alert_)))

            log_msg = "Processing profile for alert " + str(alert_)

            do_log(log_msg)

            do_log(str(rules))

            rule_df = DataFrame()

            rule_df = rules[rules['id_'].isin([int(alert_), ])]
            do_log("rule_df contains: " + str(rule_df))

            if rule_df:

                for i, row in enumerate(
                    rule_df['username'].values):

                    username = row
                    username = str(username)
                    do_log(username)

                for i, row in enumerate(
                    rule_df['user_alert_name'].values):

                    user_alert_name = row
                    user_alert_name = str(user_alert_name)
                    do_log("Found " + user_alert_name)

            try:
                #get user profile to determine alert actions
                user_profile = load_user_profile(username)

                if user_alert_actions == 'TEXT':
                    #just send an sms
                    target = user_profile['user_mobile'] + "@" + (
                        user_profile['user_carrier'])

                    send_alert(target, user_alert_name,
                        alert_out_message)
                    log_msg = "Sending TEXT to " + str(target)
                    do_log(log_msg)
                    send_alert(target, user_alert_name,
                        alert_out_message)

                if user_alert_actions == 'TEXT & EMAIL':
                    #send both sms and email

                    target = (str(user_profile['user_mobile'])
                        + "@"
                        + str(user_profile['user_carrier'])
                        + ".com")

                    log_msg = ("Sending TEXT and EMAIL to "
                        + str(target))

                    do_log(log_msg)

                    send_alert(target, user_alert_name,
                        alert_out_message)

                    target = str(user_profile['user_email'])

                    log_msg = "Sending EMAIL to " + str(target)
                    do_log(log_msg)

                    send_alert(target, user_alert_name,
                        alert_out_message)

                if user_alert_actions == 'EMAIL':

                    log_msg = "Sending EMAIL to " + str(target)
                    do_log(log_msg)

                    target = str(user_profile['user_email'])
                    send_alert(target, user_alert_name,
                        alert_out_message)

            except Exception as error:
                do_log(str(error) + " in Sending function for " + (
                    str(username) + " alert: " + str(alert_)))

    except Exception as error:
        do_log(str(error) + " in processing profile " + (
            str(username) + " alert: " + str(alert_)))
        pass


def process_message_p(in_messages_pool_q, out_messages_q, new_rules_q):
    """ Main function. Load alerts from queue then filter incoming
    messages with alert key words and conditions """

    while True:
        alerts_fired = []

        rules, sent_dict, title_dict, any_dict, \
        entities_dict, tickers_dict, any_not_dict, \
        title_not_dict, entities_not_dict, \
        tickers_not_dict = get_new_rules(new_rules_q)

        message, alert_out_message = get_new_message(in_messages_pool_q)

        alert_dict = {}

        m_title, m_description, m_sentiment, m_tickers, \
         m_entities, m_link = parse_message(message)

        alerts_fired = process_sent_dict(alert_dict, sent_dict,
         m_sentiment, alerts_fired)

        alerts_fired = process_any_dict(alert_dict, any_dict,
         m_title, m_description, alerts_fired)

        alerts_fired = process_any_not_dict(alert_dict, any_not_dict,
         m_title, m_description, alerts_fired)

        alerts_fired = process_title_dict(alert_dict, title_dict, m_title,
         alerts_fired)

        alerts_fired = process_title_not_dict(alert_dict, title_not_dict,
         m_title, alerts_fired)

        alerts_fired = process_tickers_dict(alert_dict, tickers_dict,
         m_tickers, alerts_fired)

        alerts_fired = process_tickers_not_dict(alert_dict, tickers_not_dict,
         m_tickers, alerts_fired)

        alerts_fired = process_entities_dict(alert_dict, entities_dict,
         m_entities, alerts_fired)

        alerts_fired = process_entities_not_dict(alert_dict,
         entities_not_dict, m_entities, alerts_fired)

        process_alerts_fired(alerts_fired, rules, alert_out_message)


def start_module():
    """ Setup queues and start threads and processes """

    in_messages_pool_q = Queue()
    out_messages_q = Queue()
    user_alerts_rules_q = Queue()
    new_rules_q = Queue()

    for i in range(0, 1):
        get_messages_t = threading.Thread(target=get_messages_from_kj_main_t,
            args=(UA_CONTEXT, USER_ALERTS_PULL_ADDR, in_messages_pool_q))
        get_messages_t.setDaemon(False)
        get_messages_t.start()

    for i in range(0, 1):
        load_user_alerts_t = threading.Thread(target=load_user_alerts_in_q,
            args=(user_alerts_rules_q))
        load_user_alerts_t.setDaemon(False)
        load_user_alerts_t.start()

    for i in range(0, 1):
        proc_rules_p = Process(target=parse_rules,
            args=(user_alerts_rules_q, new_rules_q,))
        proc_rules_p.start()

    for i in range(0, 1):
        proc_messages_p = Process(target=process_message_p,
            args=(in_messages_pool_q, out_messages_q, new_rules_q,))
        proc_messages_p.start()

start_module()
