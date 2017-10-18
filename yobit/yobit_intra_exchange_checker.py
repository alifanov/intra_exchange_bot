import requests

from itertools import permutations

if __name__ == "__main__":
    all_pairs = requests.get('https://yobit.net/api/3/info').json()['pairs'].keys()
    order_books = {}

    for chunk in range(0, len(all_pairs), 50):
        pairs = list(all_pairs)[chunk:chunk + 50]

        url = 'https://yobit.net/api/3/ticker/{}'.format('-'.join(pairs))
        r = requests.get(url)
        order_books.update(r.json())

    pairs_list = [p.split('_') for p in all_pairs]
    opps = []

    for ps in permutations(pairs_list, 3):
        ask = float(order_books['_'.join(ps[0])]['sell'])
        bid1 = float(order_books['_'.join(ps[1])]['buy'])
        bid2 = float(order_books['_'.join(ps[2])]['buy'])
        if ps[0][1] == ps[1][1] and ps[0][0] == ps[2][0] and ps[1][0] == ps[2][1]:
            if ask > 0:
                diff = bid1 * bid2 / ask
                if diff > 1 + 0.0075:
                    print(ps, diff)
                    print(ps[0], ask)
                    print(ps[1], bid1)
                    print(ps[2], bid2)
                    opps.append(ps)
