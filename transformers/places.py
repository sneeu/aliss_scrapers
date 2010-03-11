import datetime
import json
import time


def iso8601(value):
    return time.strftime("%Y-%m-%dT%H:%M:%S", value.timetuple()[:9])


def main():
    locs = []

    with open('transformers/ActiveScotland.json') as f:
        doc = ''.join(f.readlines())

    with open('transformers/Locations.json') as f:
        woedoc = ''.join(f.readlines())

    locations = json.loads(doc)
    woes = json.loads(woedoc)

    def find_woe(lat, lng):
        for woe in woes:
            # print woe
            if lat == woe.get('latitude') and lng == woe.get('longitude'):
                return woe['woeid']
        return None

    for location in locations.values():
        title = location['title']
        url = 'http://www.activescotland.org.uk%s' % location['url']
        addr = location['short_address']
        lat = location['lat']
        lng = location['lng']
        tags = location['tags']
        woeid = find_woe(lat, lng)
        now = datetime.datetime.now()

        locs.append({
            "_types": ["Item"], "title": title, "url": url, "locations": [woeid], "tags": tags, "_cls": "Item", "metadata": {
                "_types": ["ItemMetadata"], "last_modified": iso8601(now), "author": u"1", "_cls": "ItemMetadata", "shelflife": iso8601(now + datetime.timedelta(days=180))}})

    print json.dumps(locs)


if __name__ == '__main__':
    main()
