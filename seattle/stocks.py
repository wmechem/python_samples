'''
Find best time in trading day to buy and sell a stock
pylint 5/7
pyflakes 5/7
'''


import random


MINS_IN_TRADING_DAY = int(60*6.5)

# generate some random PRICES
PRICES = [int(1000*random.random()) for i in xrange(MINS_IN_TRADING_DAY)]
print 'Checking %s PRICES' % str(len(PRICES))


BUY_TIME = 0
SELL_TIME = 0
MAX_PROFIT = 0

for t in xrange(len(PRICES)-1):
    try:
        buy_price = PRICES[t]
        PRICES.pop(0)

        for t2 in xrange(len(PRICES)-1):
            sell_price = PRICES[t2]
            profit = sell_price - buy_price
            if profit > MAX_PROFIT:
                MAX_PROFIT = profit
                BUY_TIME = t
                SELL_TIME = t2
    except IndexError:
        print "Results:"

print 'minute in day to buy: ', BUY_TIME
print 'minute in day to sell: ', SELL_TIME
print 'max profit', MAX_PROFIT
