import scrapy
import re
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from sanic.log import logger

tag_identifiers = {
    'title': "//div[@class='fbrNcd']/a/text()",
    'image': "//a[@class='M7j9we']/div/img/@src",
    'best-price': "//div[@class='HsDfZc']/span/b/text()",
    'best-price-delivery': "//div[@class='bnNSw']/text()",
    'best-price-shop': "//div[@class='HsDfZc']/text()",  # remove ' . ' str from the return string
    'source-url': "//div[@class='fbrNcd']/a/@href",  # remove '/url?q=' str from the return string
}

spec_tag_identifiers = {
    # for headers and details use .get() method inside a loop since it contains a list of divs
    'header': "//div[@class='kBBuHb']/div/div/text()",
    'header-text': "//div[@class='kBBuHb']/div/text()",
    'details-title': "//div[@class='cQRhEd']/text()",
    'details-text': "//div[@class='MyzM8']/text()",
    'base-specs': "//div[@class='VOVcm']/text()",
}

price_tag_identifiers = {
    'price': "//div[@class='WwE9ce']/b/text()",
    'shop': "//div[@class='t9KcM']/div/a/text() | //div[@class='qEeQL']/div/a/text()",
    'delivery': "//div[@class='izR5zd']/text()",
    'url': "//div[@class='t9KcM']/div/a/@href | //div[@class='qEeQL']/div/a/@href"
}

related_tag_identifiers = {
    'title': "//div[@class='RHM0Hd']/a/text()",
    'image': "//div[@class='oR27Gd']/img/@src",
    'url': "//div[@class='RHM0Hd']/a/@href",
    'price': "//div[@class='DAPxob']/span/text()",
}

rating_tag_identifiers = {
    'text': "//div[@class='bJkpaf']/text()",
    'count': "//div[@class='vKu5p']/text()",
    'breakdown': "//div[@class='nuPC3d']/@aria-label"
}

amazon_tag_identifiers = {
    'asin': "//div[contains(@class,'s-asin')]/@data-asin",
    'price': "//span[@class='a-price']/span/text()"
}


class ProductSpider(scrapy.Spider):
    name = 'product_spider'
    allowed_domains = ['google.com', 'amazon.in']
    rule = (
        Rule(LinkExtractor(allow=('/specs/', '/offers/', '/s'))),
    )

    def __init__(self, name=None, uid=None):
        super().__init__(name)
        self.response = None
        if not uid:
            logger.warning('| spider | uid param was null - it should not be null')
            raise Exception('uid should not be null')
        self.uid = uid
        self.start_urls = [f'https://www.google.com/shopping/product/r/IN/{uid}']
        self.product = {}
        self.urls = {
            # replace the uid
            'product': f'https://www.google.com/shopping/product/r/IN/{uid}/',
            'reviews': f'https://www.google.com/shopping/product/r/IN/{uid}/reviews/',
            'offers': f'https://www.google.com/shopping/product/r/IN/{uid}#online/',
            'specs': f'https://www.google.com/shopping/product/r/IN/{uid}/specs/',
            'amazon': 'https://www.amazon.in/s?k='
        }
        self.base_url = 'https://www.google.com'
        self.amazon_url = 'https://www.amazon.in/dp/'

    def parse(self, response, **kwargs):
        logger.info('| spider | started parsing the product details')
        self.response = response
        title = self.response.xpath(tag_identifiers.get('title')).get()
        self.product = {
            'uid': self.uid,
            'analysis': None,
            'is_analysis_done': False,
            'title': title,
            'best_price': self.response.xpath(tag_identifiers.get('best-price')).get(),
            'best_price_shop': self.response.xpath(tag_identifiers.get('best-price-shop')).get().replace('\u00b7 ', ''),
            'best_price_delivery': self.response.xpath(tag_identifiers.get('best-price-delivery')).get(),
            'source_url': self.response.xpath(tag_identifiers.get('source-url')).get().replace('/url?q=', ''),
            'current_url': self.response.url,
        }
        title_sq = title.strip().replace(' ', '+')
        self.urls['amazon'] = self.urls.get('amazon') + title_sq
        self.parse_price()
        return response.follow(self.urls.get('specs'), self.parse_specs)

    def parse_specs(self, response):
        logger.info('| spider | started parsing the specs')

        header_obj = response.xpath(spec_tag_identifiers.get('header'))
        header_text_obj = response.xpath(spec_tag_identifiers.get('header-text'))
        headers = []
        if header_obj:
            for i in range(0, len(header_obj)):
                headers.append(header_obj[i].get() + header_text_obj[i].get())

        detail_title, detail_text = [], []
        details_title_obj = response.xpath(spec_tag_identifiers.get('details-title'))
        details_text_obj = response.xpath(spec_tag_identifiers.get('details-text'))
        if details_title_obj:
            for j in range(0, len(details_title_obj)):
                detail_title.append(details_title_obj[j].get())
                detail_text.append(details_text_obj[j].get())
        detail = {
            'title': detail_title,
            'text': detail_text
        }

        specs = {
            'headers': headers,
            'specifications_flat': response.xpath(spec_tag_identifiers.get('base-specs')).get(),
            'details': detail
        }
        self.product['specifications'] = specs
        return response.follow(self.urls.get('amazon'), self.parse_amazon)

    def parse_price(self):
        logger.info('| spider | started parsing the price')

        prices = []
        price_obj = self.response.xpath(price_tag_identifiers.get('price'))
        shop_obj = self.response.xpath(price_tag_identifiers.get('shop'))
        delivery_obj = self.response.xpath(price_tag_identifiers.get('delivery'))
        url_obj = self.response.xpath(price_tag_identifiers.get('url'))

        if price_obj:
            for i in range(0, len(price_obj)):
                price_json = {
                    'shop': shop_obj[i].get(),
                    'price': price_obj[i].get(),
                    'delivery': delivery_obj[i].get(),
                    'source': url_obj[i].get().replace('/url?q=', '')
                }
                prices.append(price_json)

        self.product['offers'] = prices

    def parse_rating(self):
        logger.info('| spider | started parsing the ratings')

        text = self.response.xpath(related_tag_identifiers.get('text')).get()
        count = self.response.xpath(related_tag_identifiers.get('count')).get().split(' ')[0]

        breakdown = self.response.xpath(related_tag_identifiers.get('breakdown'))
        rating_breakdown = {}
        if breakdown:
            processed_breakdowns = []
            for i in breakdown:
                processed_breakdowns.append(int(breakdown[i].get().split(' ')[0]))
            rating_breakdown = {
                'five_star': processed_breakdowns[0],
                'four_star': processed_breakdowns[1],
                'three_star': processed_breakdowns[2],
                'two_star': processed_breakdowns[3],
                'one_star': processed_breakdowns[4],
            }

        rating = {
            'rating_text': text,
            'ratings_count': count,
            'ratings_breakdown': rating_breakdown
        }

        self.product['ratings'] = rating

    def parse_related(self):
        related = []
        title = self.response.xpath(related_tag_identifiers.get('title'))
        price = self.response.xpath(related_tag_identifiers.get('price'))
        image = self.response.xpath(related_tag_identifiers.get('image'))
        url = self.response.xpath(related_tag_identifiers.get('url'))

        if title:
            for i in range(0, len(title)):
                pro = {
                    'title': title[i].get(),
                    'price': price[i].get(),
                    'image': image[i].get(),
                    'source': self.base_url + url[i].get()
                }
                related.append(pro)

        self.product['related'] = related

    def parse_amazon(self, response):
        self.product['asin'] = response.xpath(amazon_tag_identifiers.get('asin')).get()
        amazon_price = response.xpath(amazon_tag_identifiers.get('price')).get()
        delivery_status = 'Delivery charges not enclosed'
        raw = re.sub(r'[^a-zA-Z0-9]', '', amazon_price)
        if int(raw) >= 500:
            delivery_status = 'Free delivery'
        price = {
                'shop': 'amazon.in',
                'price': amazon_price,
                'delivery': delivery_status,
                'source': self.amazon_url + self.product['asin']
        }
        self.product.get('offers').append(price)
        return self.product
