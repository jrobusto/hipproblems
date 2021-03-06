import grequests
import requests
import simplejson as json
from tornado import ioloop, web


class AggregatorApiHandler(web.RequestHandler):
    def initialize(self):
        self.providers = ['expedia', 'orbitz', 'priceline', 'travelocity', 'hilton']
        self.urls = ['http://localhost:9000/scrapers/' + p for p in self.providers]

    @staticmethod
    def pick_lowest_ecstasy(lists):
        ecstasies = [l[-1]['ecstasy'] for l in lists]
        lowest = min(ecstasies)
        return ecstasies.index(lowest)

    def get(self):
        rs = (grequests.get(u) for u in self.urls)
        responses = grequests.map(rs)
        # filter out responses that indicate some sort of error occurred
        all_results = [res.json()['results'] for res in responses if res and res.status_code == 200]
        final = []
        while all_results:
            # the list is built backwards and then reversed, as popping from the end of a list is quicker
            next_index = AggregatorApiHandler.pick_lowest_ecstasy(all_results)
            final.append(all_results[next_index].pop())
            if not all_results[next_index]:
                del all_results[next_index]
        if final:
            final.reverse()
            self.write({
                "results": final,
            })
        else:
            # If no results are available, send Resource Not Available error code
            self.send_error(503)

ROUTES = [
    (r"/hotels/search", AggregatorApiHandler),
]


def run():
    app = web.Application(
        ROUTES,
        debug=True
    )

    app.listen(8000)
    print "Server (re)started. Listening on port 8000"

    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run()