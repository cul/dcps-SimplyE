# Script to parse certain information out of a crawlable OPDS feed.
import feedparser
from sheetFeeder import dataSheet
from pprint import pprint
import re
import urllib


def main():
    # TEST

    x = feed_parse(
        'https://www.gutenberg.org/ebooks/search.opds/?sort_order=downloads')

    pprint(x)

    quit()
    ###

    the_sheet = dataSheet(
        '1SyErJ6LqNUzEoJ5LP14L9Ofkn63CUaDor4H_8cRFGgo', 'test!A:Z')

    a_url = 'https://ebooks-test.library.columbia.edu/feeds/ia/culcarnegiecorp/'
    # a_url = 'https://ebooks-test.library.columbia.edu/feeds/ia/cullinglong/'

    the_dicts = feed_parse(a_url)

    the_heads = ['BIBID', 'ID', 'Title', 'URL', 'Label']

    the_data = [[
        x['id'], x['title'],
        "https://ebooks.lyrasistechnology.org/columbia/book/URI%2F" +
        urllib.parse.quote(x['id'])
    ] for x in the_dicts]

    for row in the_data:
        try:
            row.insert(0, re.search('_(.+?)_', row[0]).group(1))
        except:
            # raise "Could not parse bibid"
            print("Could not parse bibid -- " + row[0])
            row.insert(0, "")

    the_data.insert(0, the_heads)

    the_sheet.clear()
    x = the_sheet.appendData(the_data)
    print(x)


def feed_parse(url, fields=['id', 'title']):
    # Create list with top page of feed as first item.
    the_feeds = [
        feedparser.parse(url)
    ]

    # Check for "next" link in top feed.
    feed_links = the_feeds[0].feed.links
    next_link = next((x['href']
                      for x in feed_links if x['rel'] == 'next'), None)

    # If there is pagination, iterate through each page.
    while next_link:
        print('next link is: ' + next_link)
        the_feeds.append(feedparser.parse(next_link))
        feed_links = the_feeds[-1].feed.links
        next_link = next((x['href']
                          for x in feed_links if x['rel'] == 'next'), None)

    the_dicts = []

    for af in the_feeds:
        dd = [{'id': e.id, 'title': e.title} for e in af.entries]
        the_dicts += dd

    return the_dicts


if __name__ == "__main__":
    main()
