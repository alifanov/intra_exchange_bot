import time

from datetime import datetime

from itertools import chain, permutations
from poloniex import Poloniex

POLONIEX_API_KEY = ''
POLONIEX_API_SECRET = ''


polo = Poloniex(key=POLONIEX_API_KEY, secret=POLONIEX_API_SECRET)


def make_trade(pair, start_volume):
    print('[{}]: Attempt to trade'.format(datetime.now().isoformat()))
    response = polo.buy(pair['buy']['pair'], pair['buy']['price'], start_volume, orderType='fillOrKill')
    next_volume = sum([t['amount'] for t in response['resultingTrades']])
    spend = sum([t['total'] for t in response['resultingTrades']])
    print('Order #1: spend - {}'.format(spend))

    response = polo.sell(pair['sell1']['pair'], pair['sell1']['price'], next_volume, orderType='fillOrKill')
    next_volume = sum([t['total'] for t in response['resultingTrades']])
    print('Order #2: got - {}'.format(next_volume))

    response = polo.sell(pair['sell2']['pair'], pair['sell2']['price'], next_volume, orderType='fillOrKill')
    profit = sum([t['total'] for t in response['resultingTrades']])
    print('Order #3: profit - {}'.format(profit))

    print('P&L: {}'.format(profit - spend))


if __name__ == "__main__":
    while True:
        order_books = polo.returnOrderBook(depth=1)
        pairs = list(order_books.keys())
        currencies = list(set(chain(*[pair.split('_') for pair in pairs])))
        pairs_list = [p.split('_') for p in pairs]
        opps = []
        for ps in permutations(pairs_list, 3):
            ask = float(order_books['_'.join(ps[0])]['asks'][0][0])
            bid1 = float(order_books['_'.join(ps[1])]['bids'][0][0])
            bid2 = float(order_books['_'.join(ps[2])]['bids'][0][0])
            if ps[0][1] == ps[1][1] and ps[0][0] == ps[2][0] and ps[1][0] == ps[2][1]:
                diff = bid1 * bid2 / ask
                if diff > 1 + 0.0085:
                    print(ps, diff)
                    print(ps[0], ask)
                    print(ps[1], bid1)
                    print(ps[2], bid2)
                    opps.append({
                        'buy': {
                            'pair': '_'.join(ps[0]),
                            'price': ask
                        },
                        'sell1': {
                            'pair': '_'.join(ps[1]),
                            'price': bid1
                        },
                        'sell2': {
                            'pair': '_'.join(ps[2]),
                            'price': bid2
                        }
                    })
        for ps in opps:
            if ps['buy']['pair'].startswith('BTC_'):
                make_trade(ps, 0.001)
        time.sleep(2.0)
