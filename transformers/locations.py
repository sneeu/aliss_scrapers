import json
import Queue
import threading
from urlparse import urlparse, parse_qs
import urllib2

from BeautifulSoup import BeautifulSoup

from soupselect import select as css


URL_TEMPLATE = 'http://www.geomojo.org/cgi-bin/reversegeocoder.cgi?lat=%s&long=%s'


NUMBER_OF_WORKERS = 10
TIMEOUT=15
work_queue = Queue.Queue()
data = {}
data_lock = threading.Lock()


def do_work(*args):
    location = args[0]
    # print location
    lat, lng, address = location['lat'], location['lng'], location['short_address']

    url = URL_TEMPLATE % (lat, lng)

    data_lock.acquire()
    print url
    data_lock.release()

    xml = ''.join(urllib2.urlopen(url, timeout=TIMEOUT).readlines())
    soup = BeautifulSoup(xml)

    woeid = None
    try:
        woeid = css(soup, 'woeid')[0].contents[0]
        placetype = css(soup, 'type')[0].contents[0]
    except Exception, e:
        print e

    item = {"lat_lon": [lat, lng], "latitude": lat, "longitude": lng, "_types": ["Location"], "name": address, "woeid": woeid, "placetype": placetype, "_cls": "Location"}

    data_lock.acquire()
    print '.'
    data.append(item)
    data_lock.release()


def worker():
    while True:
        item = work_queue.get()
        try:
            do_work(*item)
        except:
            pass
        work_queue.task_done()


def main():
    """Application entry point."""
    urllib2.install_opener(urllib2.build_opener())

    for __ in range(NUMBER_OF_WORKERS):
        t = threading.Thread(target=worker)
        t.setDaemon(True)
        t.start()

    with open('transformers/ActiveScotland.json') as f:
        doc = ''.join(f.readlines())
        locations = json.loads(doc)

    for location in locations.values():
        lat = location.get('lat', None)
        lng = location.get('lng', None)
        if lat and lng:
            work_queue.put([location])

    work_queue.join()
    print json.dumps(data)


if __name__ == '__main__':
    main()
