import scrapy
from sanic.log import logger

reviews_tag_identifier = "//span[@data-hook='review-body']/span/text()"
next_page_tag_identifier = "//li[@class='a-last']/a/@href"


class AmazonSpider(scrapy.Spider):
    name = 'amazon_spider'
    allowed_domains = ['amazon.in']

    def __init__(self, name=None, uid=None, asin=None):
        super().__init__(name)
        if not asin:
            logger.warning('| amazon spider | asin param was null - it should not be null')
            raise Exception('asin should not be null')
        self.asin = asin
        self.uid = uid
        self.start_urls = [
            f'https://www.amazon.in/product-reviews/{asin}'
        ]
        self.reviews = []
        self.base_url = 'https://www.google.com'

    def parse(self, response, **kwargs):
        logger.info('| amazon spider | started parsing the reviews')
        reviews_dom = response.xpath(reviews_tag_identifier)
        if reviews_dom:
            for review in reviews_dom:
                self.reviews.append(
                    review.get()
                )
        else:
            logger.warning('| amazon spider | No reviews element in the html page')

        next_page = response.xpath(next_page_tag_identifier).get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page), self.parse
            )
        else:
            yield {
                'meta-data': {
                    'uid': self.uid,
                    'asin': self.asin,
                    'is_preprocessed': False,
                    'total_reviews': len(self.reviews),
                },
                'reviews': self.reviews
            }
