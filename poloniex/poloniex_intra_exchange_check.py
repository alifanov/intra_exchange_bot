import time

from datetime import datetime

from itertools import chain, permutations
from poloniex import Poloniex, PoloniexError

from config import POLONIEX_API_KEY, POLONIEX_API_SECRET


polo = Poloniex(key=POLONIEX_API_KEY, secret=POLONIEX_API_SECRET)

VOLUME_COEFF = 0.8

MIN_AMOUNT = 0.0001


def make_trade(pair, balance):

    volume = balance / pair['buy']['price']
    volume *= (1.0 - 0.0025)
    volume = min(volume, pair['buy']['volume'])
    start_volume = volume * VOLUME_COEFF

    print('[{}]: Attempt to trade with volume: {}'.format(datetime.now().isoformat(), start_volume))
    if pair['buy']['price'] * start_volume < MIN_AMOUNT:
        print('Too small volume for buy: price: {}, balance: {}, vol: {}, trade vol: {}'.format(pair['buy']['price'], balance, start_volume, pair['buy']['volume']))
        return -1
    if pair['sell1']['price'] * pair['sell1']['volume'] * (1.0 - 0.0025) < MIN_AMOUNT:
        print('Too small volume for sell1')
        return -1
    if pair['sell2']['price'] * pair['sell2']['volume'] * (1.0 - 0.0025) < MIN_AMOUNT:
        print('Too small volume for sell2')
        return -1
    response = polo.buy(pair['buy']['pair'], pair['buy']['price'], start_volume, orderType='fillOrKill')
    print(response)

    next_volume = sum([float(t['amount']) for t in response['resultingTrades']])
    spend = sum([float(t['total']) for t in response['resultingTrades']])
    print('Order #1: spend - {}'.format(spend))

    next_volume = min(next_volume, pair['sell1']['volume'])
    rate = pair['sell1']['price']
    volume = next_volume * (1.0 - 0.0025)

    while True:
        try:
            response = polo.sell(pair['sell1']['pair'], rate, volume, orderType='fillOrKill')
            break
        except PoloniexError as e:
            if 'Total must be at least' in str(e):
                return 0 - spend
            elif 'Not enough ' in str(e):
                next_volume *= 0.99  # decrease volume for 1%
            else:
                rate *= 0.999
    print(response)

    next_volume = sum([float(t['total']) for t in response['resultingTrades']])
    print('Order #2: got - {}'.format(next_volume))
    next_volume = min(next_volume, pair['sell2']['volume'])
    rate = pair['sell2']['price']
    volume = next_volume * (1.0 - 0.0025)

    while True:
        try:
            response = polo.sell(pair['sell2']['pair'], rate, volume, orderType='fillOrKill')
            break
        except PoloniexError as e:
            if 'Total must be at least' in str(e):
                return 0 - spend
            elif 'Not enough ' in str(e):
                next_volume *= 0.99  # decrease volume for 1%
            else:
                rate *= 0.999

    print(response)
    profit = sum([float(t['total']) for t in response['resultingTrades']])
    print('Order #3: profit - {}'.format(profit))

    print('P&L: {}'.format(profit - spend))
    print('ROI: {:.4%}'.format((profit - spend) / spend))
    return profit - spend


def arbitrage():
    balances = polo.returnBalances()
    print('Start balance: {} BTC'.format(balances['BTC']))

    while True:
        order_books = polo.returnOrderBook(depth=2)
        pairs = list(order_books.keys())
        pairs_list = [p.split('_') for p in pairs]
        opps = []
        for ps in permutations(pairs_list, 3):
            ask = float(order_books['_'.join(ps[0])]['asks'][0][0])
            vol0 = float(order_books['_'.join(ps[0])]['asks'][0][1])

            bid1 = float(order_books['_'.join(ps[1])]['bids'][0][0])
            vol1 = float(order_books['_'.join(ps[1])]['bids'][0][1])

            bid2 = float(order_books['_'.join(ps[2])]['bids'][0][0])
            vol2 = float(order_books['_'.join(ps[2])]['bids'][0][1])
            if ps[0][1] == ps[1][1] and ps[0][0] == ps[2][0] and ps[1][0] == ps[2][1]:
                diff = bid1 * bid2 / ask
                if diff > 1 + 0.0085:
                    print(datetime.now(), ps, diff)
                    trade = {
                        'buy': {
                            'pair': '_'.join(ps[0]),
                            'price': ask,
                            'volume': vol0
                        },
                        'sell1': {
                            'pair': '_'.join(ps[1]),
                            'price': bid1,
                            'volume': vol1
                        },
                        'sell2': {
                            'pair': '_'.join(ps[2]),
                            'price': bid2,
                            'volume': vol2
                        }
                    }
                    # opps.append(trade)
                    if trade['buy']['pair'].startswith('BTC_'):
                        profit = make_trade(trade, float(balances['BTC']))
                        if profit != -1:
                            return
        time.sleep(2.0)


if __name__ == "__main__":
    arbitrage()