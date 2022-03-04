import asyncio
import urllib.request

from app.scrapper import product_extractor
from app.scrapper.review_extractor import ReviewExtractor
from app.scrapper.search_extractor import SearchExtractor


def run():
    pe = product_extractor.ProductExtractor('7596414811817512508')
    resp = asyncio.run(pe.extract())
    print(resp)


def test():
    re = ReviewExtractor('8829305278559966706')
    resp = asyncio.run(re.extract())
    print(resp)


def process():
    se = SearchExtractor('realme 8')
    se = asyncio.run(se.extract())
    print(se)


def test_run():
    url = 'https://google.com/search?q=Where+can+I+get+the+best+coffee'

    # Perform the request
    request = urllib.request.Request(url)

    # Set a normal User Agent header, otherwise Google will block the request.
    request.add_header('User-Agent',
                       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/87.0.4280.88 Safari/537.36')
    raw_response = urllib.request.urlopen(request).read()

    # Read the repsonse as a utf-8 string
    html = raw_response.decode("utf-8")
    print(html)


if __name__ == '__main__':
    run()
