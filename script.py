import asyncio
import json
import os.path
from json import JSONDecodeError

import tensorflow as tf
from scrapy.crawler import CrawlerProcess
from app.scrapper.spiders.amazon_spider import AmazonSpider
from app.services.analyzer_service import Analyzer


def run():
    if os.path.exists('reviews.json'):
        with open('reviews.json') as json_file:
            try:
                reviews = json.load(json_file)
            except JSONDecodeError:
                reviews = None
                pass

    if not reviews:
        cr = CrawlerProcess({
            'ITEM_PIPELINES': {
                'app.scrapper.pipelines.ReviewPipeline': 300
            },
        })
        cr.crawl(AmazonSpider, uid='12976475649125200916', asin='B07XR98DGP')
        cr.start()
    else:
        analyzer = Analyzer(
            meta_data=reviews.get('meta-data'),
            reviews=reviews.get('reviews')
        )
        asyncio.run(analyzer.analyze())


def test():
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))


if __name__ == '__main__':
    run()
