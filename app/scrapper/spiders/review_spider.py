import scrapy
from sanic.log import logger

review_tag_identifier = "//div[@class='Rw0r3e']/div[last()]"
next_page_tag_identifier = "//a[@class='PNHYKd']/@href"


class ReviewSpider(scrapy.Spider):

    name = 'review_spider'
    allowed_domains = ['google.com']

    def __init__(self, name=None, uid=None):
        super().__init__(name)
        if not uid:
            logger.warning('| spider | uid param was null - it should not be null')
            raise Exception('uid should not be null')
        self.uid = uid
        self.start_urls = [
            f'https://www.google.com/shopping/product/r/IN/{uid}/reviews'
        ]
        self.reviews = []
        self.base_url = 'https://www.google.com'

    def parse(self, response, **kwargs):
        logger.info('| review spider | started parsing the reviews')
        review_obj = response.xpath(review_tag_identifier)
        if review_obj:
            for review in review_obj:
                self.reviews.append(
                    review.get().replace('<div>', '').replace('</div>', '')
                )

        next_page = response.xpath(next_page_tag_identifier).get()
        if next_page:
            next_page_url = self.base_url + next_page
            yield scrapy.Request(
                response.urljoin(next_page_url), self.parse
            )
        else:
            yield {
                'meta-data': {
                    'uid': self.uid
                },
                'reviews': self.reviews
            }
