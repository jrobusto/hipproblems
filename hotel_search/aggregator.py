import grequests
import requests
import simplejson as json
from tornado import gen, ioloop, web


def pick_lowest_ecstasy(lists):
    ecstasies = [l[-1]['ecstasy'] for l in lists]
    lowest = min(ecstasies)
    return ecstasies.index(lowest)

providers = ['expedia', 'orbitz', 'priceline', 'travelocity', 'hilton']
urls = ['http://localhost:9000/scrapers/' + p for p in providers]

rs = (grequests.get(u) for u in urls)

responses = grequests.map(rs)#[requests.get('http://localhost:9000/scrapers/' + p) for p in providers]

all_results = [res.json()['results'] for res in responses]

final = []
while all_results:
    next_index = pick_lowest_ecstasy(all_results)
    final.append(all_results[next_index].pop())
    if not all_results[next_index]:
        del all_results[next_index]


print final