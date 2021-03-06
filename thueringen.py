#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# A Studentenwerk Thüringen Mensa scraper, producing XML for openmensa.org.

import sys; reload(sys)
sys.setdefaultencoding('utf-8')

from cgi import escape
from datetime import datetime, timedelta

from requests import get
from bs4 import BeautifulSoup

MENSEN = {

    # Jena
    'Ernst-Abbe-Platz': 'jena/mensa-ernst-abbe-platz',
    'Philosophenweg': 'jena/mensa-philosophenweg',
    'Carl-Zeiss-Promenade': 'jena/mensa-carl-zeiss-promenade',
    'vegeTable': 'jena/vegetable',
    'Cafeteria Bibliothek (ThulB)': 'jena/cafeteria-bibliothek-thulb',

    # 'Weimar': 'weimar'
    'Mensa am Park': 'weimar/mensa-am-park',

    # Eisenach
    'Mensa am Wartenberg': 'eisenach/mensa-am-wartenberg-2',

    # Erfurt
    'Nordhäuser Straße': 'erfurt/mensa-nordhaeuser-strasse',
    'Altonaer Straße': 'erfurt/mensa-altonaer-strasse',

    # Gera
    'Studienakademie Gera': 'gera/mensa-berufsakademie-gera',

    # Ilmenau
    'Ehrenberg': 'ilmenau/mensa-ehrenberg',
    'NANOteria': 'ilmenau/cafeteria-nanoteria',
}


def extract(html, mensa='eabp', day=0):
    """Extract meals from HTML and yielding them as dictlike-object."""

    soup = BeautifulSoup(html)
    div = soup.find('div', id="day_%i" % (day+2))

    # hidden in there as triple -> (müll, name, price)
    td = div.table.find_all('td') if div and div.table else []

    for i in range(0, len(td), 3):
        yield type('Meal', (object, ), {
            'name': next(td[i+1].stripped_strings),
            'note': "",
            'price': td[i+2].text.strip().replace(',', '.').rstrip(' €') or '0.00'
        })()


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'Usage: %s MENSA' % sys.argv[0]
        sys.exit(1)

    try:
        mensa = [key for key in MENSEN if key.lower().startswith(sys.argv[1].lower())][0]
        abbr = MENSEN[mensa]
    except IndexError:
        print '%s is not available. Try %s' % (sys.argv[1], ', '.join(MENSEN.keys()))
        sys.exit(1)

    print '<?xml version="1.0" encoding="UTF-8"?>'
    print '<openmensa version="2.0"'
    print            'xmlns="http://openmensa.org/open-mensa-v2"'
    print            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    print            'xsi:schemaLocation="http://openmensa.org/open-mensa-v2 http://openmensa.org/open-mensa-v2.xsd">'

    r = get('http://www.stw-thueringen.de/deutsch/mensen/einrichtungen/%s.html' % abbr)
    print '  <canteen>'

    for day in range(5):
        print '    <day date="%s">' % (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')

        meals = list(extract(r.content, abbr, day))
        if not meals:
            print '      <closed />'

        for i, meal in enumerate(meals):
            print '      <category name="Essen %i">' % (i+1)
            print '        <meal>'
            print '          <name>' + escape(meal.name) + '</name>'
            if meal.note:
                print '          <note>' + escape(meal.note) + '</note>'
            print '          <price role="student">' + meal.price + '</price>'
            print '        </meal>'
            print '      </category>'
        print '    </day>'
    print '  </canteen>'
    print '</openmensa>'
