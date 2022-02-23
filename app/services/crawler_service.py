from scrapy.crawler import CrawlerProcess
from app.scrapper.spiders.amazon_spider import AmazonSpider
from app.scrapper.spiders.product_spider import ProductSpider


async def crawl_product(uid):
    crawler = CrawlerProcess({
        'ITEM_PIPELINES': {
            'app.scrapper.pipelines.ProductPipeline': 300
        }
    })
    crawler.crawl(ProductSpider, uid=uid)
    crawler.start()


def crawl_reviews(uid, asin):
    cr = CrawlerProcess({
        'ITEM_PIPELINES': {
            'app.scrapper.pipelines.ReviewPipeline': 800
        }
    })
    cr.crawl(AmazonSpider, uid=uid, asin=asin)
    cr.start()
