"""
This module establishes a connection to a twitter stream and filters
based on stock symbol. Incoming tweets are sent via zeroMQ to the main
finRocket process to be analyzed and stored.

Demo only - no warranty implied or otherwise - libraries may be deprecated etc.

pylint 9.56/10 2016/05/14
flake8 2016/05/14 continuation line under-indented for visual indent
"""
from datetime import datetime
import logging
import os
import sys
import threading
import time

from birdy.twitter import StreamClient
from pandas.io.data import read_csv
import zmq

HOME_DIR = os.environ['HOME']

VERBOSE = 0

logging.basicConfig(
    filename=HOME_DIR + "/kj_tweets_stocks.log", level=logging.DEBUG)

# setup zmq push
CONTEXT = zmq.CONTEXT()

TWITTER_PUB_ADDR = 'tcp://127.0.0.1:6050'
FR_RCV_ADDR = 'tcp://127.0.0.1:6051'

# twitter access codes
# need these in real life :)

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''

TWITTER_SOURCES_FILE = "nasdaq_finance_400_2014_05_20.csv"
TWITTER_SOURCES = read_csv(TWITTER_SOURCES_FILE)


def gen_follow_symbols():
    """ Create a list of symbols to follow from the csv file """
    follow_syms = []
    for i, ticker in enumerate(TWITTER_SOURCES.Symbol.values):
        ticker = "$" + str(ticker)
        follow_syms.append(ticker)
        return follow_syms


def get_ticker_info(data):
    """ Lookup symbol's sector in Nasdaq """
    m_class = TWITTER_SOURCES[
                TWITTER_SOURCES['Symbol'].str.contains(
                str(data['entities']['symbols']))]['Sector'].values
    if not m_class:
        m_class = []

    symbols = []
    sym_list = data['entities']['symbols']
    i_max = len(sym_list)
    for i in range(0, i_max):
        symbol = sym_list[i]['text']
        symbols.append(symbol)

    if not symbols:
        symbols = []

    return m_class, symbols


def format_tweet(data):
    """ Make the finRocket standard message for each tweet. """

    time_tmp = time.strptime(
                data['created_at'], "%a %b %d %H:%M:%S + 0000 %Y")

    time_tmp = time.mktime(time_tmp)
    date_time_ = datetime.fromtimestamp(time_tmp)
    twit_date_time = str(date_time_)
    m_class, symbols = get_ticker_info(data)
    m_description = data['text'].encode(
                encoding='utf-8', errors='ignore')
    m_title = str(
                data['user']['name']) + ": "
                    + data['text'].encode(
                        encoding='utf-8', errors='ignore')
    m_proc_time = str(datetime.now())
    m_source = "@" + str(data['user']['screen_name'])
                            + ": "
                            + str(data['user']['name'])
    m_region = data['user']['location']
    m_link = str('http://twitter.com/') + str(
                data['user']['screen_name'])

    tweet_msg = {
             "m_description": m_description,

             "m_title": m_title,
             "m_pub_date": twit_date_time,

             "m_proc_time": m_proc_time,
             "m_channel": "twitter",

             "m_source": m_source,

             "m_feedparsed": m_proc_time,
             "m_host": "KJ Host",
             "m_class": m_class,
             "m_tickers": symbols,
             "m_region": m_region,

             "m_link": m_link

             }

    console_text = str(m_title + " " + (
            str(twit_date_time) + " "
            + str(symbols])
            + str("\n"))

    sys.stdout.write(console_text)
    sys.stdout.flush()
    return tweet_msg


def send_tweet(tweet_pub_socket, tweet_msg):
    """ Send to main module via ZeroMQ """
    tweet_pub_socket.send_pyobj(tweet_msg)

    l_string = str(datetime.now()) + (
        "Sent tweet to KJ_MAIN")
    logging.info(l_string)


def process_tweets(response, tweet_pub_socket):
    """ Get tweets from stream, process and send to main module. """

    while True:
        for data in response.stream():

            try:
                tweet_msg = format_tweet(data)
                send_tweet(tweet_pub_socket, tweet_msg)

            except Exception as error:
                l_string = str(datetime.now()) + (
                        "Failed to process tweet" +
                        str(error))

                logging.info(l_string)
    return


def make_twitter_connection(context, twitter_pub_addr):
    """ setup twitter and ZeroMQ connections. """
    client = StreamClient(CONSUMER_KEY,
                    CONSUMER_SECRET,
                    ACCESS_TOKEN,
                    ACCESS_TOKEN_SECRET)

    #setup listener for twitter
    follow_syms = gen_follow_symbols()
    response = client.stream.statuses.filter.post(track=follow_syms)
    l_string = str(datetime.now()) + (
        " Thread called twitter agent ")
    logging.info(l_string)

    try:
        context = context
        tweet_pub_socket = context.socket(zmq.PUB)
        tweet_pub_socket.connect(twitter_pub_addr)
        sys.stdout.write("Initialized twitter_zmq_push \n")
        sys.stdout.flush()
        l_string = str(datetime.now()) + (
            "init twitter_zmq_push success")
        logging.info(l_string)

    except Exception as error:
        l_string = str(datetime.now()) + (
            "Failed to init twitter_zmq_push error: " + str(error))
        logging.info(l_string)

    process_tweets(response, tweet_pub_socket)

    return


def start_module():
    """ Start module """

    for i in range(0, 10):
        twitter_agent_thread = threading.Thread(
            target=make_twitter_connection, args=(CONTEXT, TWITTER_PUB_ADDR))
        twitter_agent_thread.setDaemon(False)
        twitter_agent_thread.start()


start_module()
