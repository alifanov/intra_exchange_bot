import time
from itertools import chain, permutations
import ccxt

if __name__ == "__main__":
    exchange = ccxt.bitfinex2()
    pairs = exchange.symbols

    currencies = list(set(chain(*[pair.split('/') for pair in pairs])))
    pairs_list = [p.split('/') for p in pairs]

    opps = []
    for ps in permutations(pairs_list, 3):
        order_books = {}
        for p in ps:
            p = '/'.join(p)
            order_books[p] = exchange.fetch_ticker(p)
        ask = float(order_books['/'.join(ps[0])]['ask'])
        bid1 = float(order_books['/'.join(ps[1])]['bid'])
        bid2 = float(order_books['/'.join(ps[2])]['bid'])
        if ps[0][0] == ps[1][0] and ps[1][1] == ps[2][0] and ps[0][1] == ps[2][1]:
            diff = bid1 * bid2 / ask
            if diff > 1 + 0.0075:
                print(ps, diff)
                print(ps[0], ask)
                print(ps[1], bid1)
                print(ps[2], bid2)
                opps.append(ps)
        time.sleep(1)
