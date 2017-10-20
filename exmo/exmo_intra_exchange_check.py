from itertools import chain, permutations
import requests

if __name__ == "__main__":
    pairs = requests.get('https://api.exmo.com/v1/pair_settings/').json().keys()
    pairs = list(pairs)

    order_books = requests.get('https://api.exmo.com/v1/order_book/?pair={}&limit=1'.format(','.join(pairs))).json()
    currencies = list(set(chain(*[pair.split('_') for pair in pairs])))
    pairs_list = [p.split('_') for p in pairs]

    opps = []
    for ps in permutations(pairs_list, 3):
        ask = float(order_books['_'.join(ps[0])]['ask_top'])
        bid1 = float(order_books['_'.join(ps[1])]['bid_top'])
        bid2 = float(order_books['_'.join(ps[2])]['bid_top'])
        if ps[0][0] == ps[1][0] and ps[1][1] == ps[2][0] and ps[0][1] == ps[2][1]:
            diff = bid1 * bid2 / ask
            if diff > 1 + 0.0075:
                print(ps, diff)
                print(ps[0], ask)
                print(ps[1], bid1)
                print(ps[2], bid2)
                opps.append(ps)
