import Queue
import threading
from urlparse import urlparse, parse_qs
import urllib2

from BeautifulSoup import BeautifulSoup

from soupselect import select as css


LOCATIONS = ['eh%d' % d for d in range(1, 2)]
URL_TEMPLATE = 'http://www.activescotland.org.uk/search/results.html?location=%s&new=true&resultsPerPage=100'


NUMBER_OF_WORKERS = 1
work_queue = Queue.Queue()
screen_lock = threading.Lock()


def do_work(*args):
    url = args[0]
    html = ''.join(urllib2.urlopen(url, timeout=5).readlines())
    soup = BeautifulSoup(html)

    for listitem in css(soup, 'li.listitem'):
        title = url = short_address = phone = lat = lng = None
        activities = []
        t = css(listitem, 'h3 a')
        if t:
            title = t[0].contents[0]
            url = t[0]['href']
        sa = css(listitem, 'li.shortaddress')
        if sa:
            short_address = sa[0].contents[0]
        pn = css(listitem, 'li.phonenumber')
        if pn:
            phone = pn[0].contents[0]
        for im in css(listitem, 'div.activityicons img'):
            activities.append(im['title'])

        img = css(listitem, 'div.listmap img[alt^=Map]')
        if img:
            ll = parse_qs(urlparse(img[0]['src']).query)
            lat, lng = ll['lat'][0], ll['lng'][0]

        screen_lock.acquire()
        print title, lat, lng, url, phone, short_address, ', '.join(activities)
        screen_lock.release()


def worker():
    while True:
        item = work_queue.get()
        do_work(*item)
        work_queue.task_done()


def main():
    """Application entry point."""
    urllib2.install_opener(urllib2.build_opener())

    for __ in range(NUMBER_OF_WORKERS):
        t = threading.Thread(target=worker)
        t.setDaemon(True)
        t.start()

    for location in LOCATIONS:
        url = URL_TEMPLATE % location
        work_queue.put([url])

    work_queue.join()


if __name__ == '__main__':
    main()
