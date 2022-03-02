import asyncio

from app.scrapper import product_extractor
from app.scrapper.review_extractor import ReviewExtractor


def run():
    pe = product_extractor.ProductExtractor('8829305278559966706')
    resp = asyncio.run(pe.extract())
    print(resp)


def test():
    re = ReviewExtractor('8829305278559966706')
    resp = asyncio.run(re.extract())
    print(resp)


def process():
    pass


if __name__ == '__main__':
    test()
