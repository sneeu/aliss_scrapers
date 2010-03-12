import json
import re
import sys
import Queue
import threading
import urllib2

from BeautifulSoup import BeautifulSoup

from soupselect import select as css


TIMEOUT = 15
URL_TEMPLATE = "http://www.grampiancaredata.gov.uk/development/keyword-search/?tx_evgcdsearch_pi1%%5Breport%%5D=gcd_search&tx_evgcdsearch_pi1%%5Bstart%%5D=%d"


LOCK = threading.Lock()


data = {}


def do_work(*args):
    # Do something with args
    url = args[0]

    with LOCK:
        print url

    html = ''.join(urllib2.urlopen(url, timeout=TIMEOUT).readlines())
    html = html.replace('<!- Google Analytics -->', '')
    html = re.sub('<script.*?>[\s\S]*?</.*?script>', '', html)
    soup = BeautifulSoup(html)

    item = {}

    def parse(listitem):
        title = ident = web = short_address = phone = lat = lng = None
        tags = []

        t = css(listitem, 'h1 a')
        if t:
            title = t[0].contents[0]
            ident = t[0]['href']

        t = css(listitem, '.tel-fax .record-detail')
        if t:
            phone = t[0].contents[1].strip()

        t = css(listitem, '.web a[href^=http]')
        if t:
            web = t[0]['href']

        t = css(listitem, '.p-code .record-detail')
        if t:
            short_address = str(t[0].contents[1]).strip()

        item = {
            'title': title,
            'lat': lat,
            'lng': lng,
            'url': web,
            'phone': phone,
            'short_address': short_address,
            'tags': tags,
            'origin': ident
        }

        with LOCK:
            sys.stdout.write('.')
            data[ident] = item

    for listitem in css(soup, '.search-row-grey-wrapper'):
        parse(listitem)

    for listitem in css(soup, '.search-row-white-wrapper'):
        parse(listitem)


number_of_workers = 5
work_queue = Queue.Queue()


def worker():
    while True:
        item = work_queue.get()
        try:
            do_work(*item)
        except Exception, e:
            print e
        work_queue.task_done()


def main():
    urllib2.install_opener(urllib2.build_opener())

    for __ in range(number_of_workers):
        t = threading.Thread(target=worker)
        t.setDaemon(True)
        t.start()

    max_result = 1945
    # max_result = 24

    for item in (URL_TEMPLATE % n for n in xrange(0, max_result, 25)):
        work_queue.put([item])

    work_queue.join()
    print json.dumps(data)


if __name__ == '__main__':
    main()
