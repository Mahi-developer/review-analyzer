import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from sanic.log import logger
from lxml import etree
from app.utils.utils import process_integer_from_string, separate_shop_name, separate_uid_from_url
from utils.config import environ_config

tag_identifiers = {
    'title': "//div[@class='fbrNcd']/a",
    'image': "//a[@class='M7j9we']/div/img/@src",
    'best-price': "//div[@class='HsDfZc']/span/b",
    'best-price-delivery': "//div[@class='bnNSw']",
    'best-price-shop': "//a[@class='VLRGse']/@aria-label",  # remove ' . ' str from the return string
    'source-url': "//div[@class='fbrNcd']/a/@href",  # remove '/url?q=' str from the return string
}

spec_tag_identifiers = {
    # for headers and details use .get() method inside a loop since it contains a list of divs
    'header': "//div[@class='kBBuHb']",
    'header-text': "//div[@class='kBBuHb']/div",
    'details-title': "//div[@class='cQRhEd']",
    'details-text': "//div[@class='MyzM8']",
    'base-specs': "//div[@class='VOVcm']",
}

price_tag_identifiers = {
    'price': "/div[@class='WwE9ce']/b",
    'shop': "//div[@class='t9KcM']/div/a | //div[@class='qEeQL']/div/a",
    'base': "//div[@class='OF7I2d']",
    'delivery': "/div[@class='izR5zd']",
    'url': "//div[@class='t9KcM']/div/a/@href | //div[@class='qEeQL']/div/a/@href"
}

related_tag_identifiers = {
    'title': "//div[@class='RHM0Hd']/a",
    'image': "//div[@class='oR27Gd']/img/@src",
    'url': "//div[@class='RHM0Hd']/a/@href",
    'price': "//div[@class='DAPxob']/span",
}

rating_tag_identifiers = {
    'text': "//div[@class='bJkpaf']",
    'count': "//div[@class='vKu5p']",
    'breakdown': "//div[@class='nuPC3d']/@aria-label"
}

amazon_tag_identifiers = {
    'asin': "//div[contains(@class,'s-asin')]/@data-asin",
    'price': "//span[@class='a-price']/span"
}


class ProductExtractor:
    def __init__(self, uid):
        self.dom = None
        self.soup = None
        if not uid:
            logger.warning(f'| {self.__class__.__name__} | uid param was null - it should not be null')
            raise Exception('uid should not be null')
        self.uid = uid
        self.product = {}
        self.urls = {
            # replace the uid
            'product': f'https://www.google.com/shopping/product/{uid}/',
            'reviews': f'https://www.google.com/shopping/product/{uid}/reviews/',
            'offers': f'https://www.google.com/shopping/product/{uid}#online/',
            'specs': f'https://www.google.com/shopping/product/{uid}/specs/',
            'amazon': 'https://www.amazon.in/s?k='
        }
        self.base_url = 'https://www.google.com'
        self.amazon_url = 'https://www.amazon.in/dp/'
        self.alter_url = f'https://www.google.com/shopping/product/1?prds=pid:{uid}'
        self.headers = (
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'
            }
        )
        self.session = requests.session()

    async def extract(self, url=None):
        if not url:
            url = self.urls.get('product')
        with self.session.get(url, headers=self.headers) as response:
            if response.status_code == 200:
                await self.parse(response)
            else:
                return {
                    'status': 'Unable to get product details',
                    'dom': response,
                }
        return self.product

    async def parse(self, response):
        logger.info(f'| {self.__class__.__name__} | started parsing the product details')
        self.soup = BeautifulSoup(response.content, "html.parser")
        self.dom = etree.HTML(str(self.soup))
        try:
            title = self.dom.xpath(tag_identifiers.get('title'))[0].text
            shop = self.dom.xpath(tag_identifiers.get('best-price-shop'))[0]
            if 'Visit site of ' in shop:
                shop = shop.replace('Visit site of ', '')
            self.product = {
                'uid': self.uid,
                'analysis': None,
                'is_analysis_done': False,
                'title': title,
                'best_offer': {
                    'price': process_integer_from_string(self.dom.xpath(tag_identifiers.get('best-price'))[0].text),
                    'shop': separate_shop_name(shop),
                    'delivery': self.dom.xpath(tag_identifiers.get('best-price-delivery'))[0].text,
                    'url': self.dom.xpath(tag_identifiers.get('source-url'))[0].replace('/url?q=', ''),
                },
                'image': self.dom.xpath(tag_identifiers.get('image'))[0],
                'url': environ_config.UI_URLS.get('product') + self.uid
            }
            title_sq = quote_plus(title.strip())
            self.urls['amazon'] = self.urls.get('amazon') + title_sq.replace('-', '')
            await self.parse_price()
            await self.parse_rating()
            await self.parse_related()
            with self.session.get(self.urls.get('specs'), headers=self.headers) as response:
                if response.status_code == 200:
                    await self.parse_specs(response)
            return self.product
        except IndexError:
            await self.extract(self.alter_url)
        return None

    async def parse_specs(self, response):
        logger.info(f'| {self.__class__.__name__} | started parsing the specs')
        soup = BeautifulSoup(response.content, "html.parser")
        dom = etree.HTML(str(soup))
        header_obj = soup.findAll('div', class_='kBBuHb')
        headers = []
        if header_obj:
            for i in header_obj:
                headers.append(i.text)

        detail_title, detail_text = [], []
        details_title_obj = dom.xpath(spec_tag_identifiers.get('details-title'))
        details_text_obj = dom.xpath(spec_tag_identifiers.get('details-text'))
        if details_title_obj:
            for j in range(0, len(details_title_obj)):
                detail_title.append(details_title_obj[j].text)
                detail_text.append(details_text_obj[j].text)
        detail = {
            'title': detail_title,
            'text': detail_text
        }

        spec_flat = None
        spec_flat_div = soup.findAll('div', class_='VOVcm')
        if len(spec_flat_div) > 0:
            spec_flat = spec_flat_div[1].text

        specs = {
            'headers': headers,
            'specifications_flat': spec_flat,
            'details': detail
        }
        self.product['specifications'] = specs

    async def parse_price(self):
        logger.info(f'| {self.__class__.__name__} | started parsing the price')
        prices = []
        div = self.soup.findAll('div', class_='t9KcM')
        if div:
            for i in div:
                delivery = i.find('div', class_='izR5zd')
                if delivery:
                    delivery = delivery.text
                price_json = {
                    'shop': separate_shop_name(i.find('a').text),
                    'price': process_integer_from_string(i.find('div', class_='WwE9ce').text),
                    'delivery': delivery,
                    'source': i.find('a')['href'].replace('/url?q=', '')
                    }
                prices.append(price_json)

        self.product['offers'] = prices

    async def parse_rating(self):
        logger.info(f'| {self.__class__.__name__} | started parsing the ratings')

        text, count = None, None
        t = self.dom.xpath(rating_tag_identifiers.get('text'))
        if t:
            text = t[0].text
        c = self.dom.xpath(rating_tag_identifiers.get('count'))
        if c:
            count = c[0].text.split(' ')[0]

        breakdown = self.dom.xpath(rating_tag_identifiers.get('breakdown'))
        rating_breakdown = {}
        if breakdown:
            processed_breakdowns = []
            for i in breakdown:
                processed_breakdowns.append(process_integer_from_string(i.split(' ')[0]))
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

    async def parse_related(self):
        related = []
        related_div = self.soup.findAll('div', class_='r240Sd')
        # title = self.dom.xpath(related_tag_identifiers.get('title'))
        # price = self.dom.xpath(related_tag_identifiers.get('price'))
        # image = self.dom.xpath(related_tag_identifiers.get('image'))
        # url = self.dom.xpath(related_tag_identifiers.get('url'))

        if related_div:
            for i in related_div:
                url = i.find('a')['href']
                pro = {
                    'title': i.find('div', class_='RHM0Hd').text,
                    'price': process_integer_from_string(i.find('span', class_='wuySkd').text),
                    'image': i.find('img')['src'],
                    'source': self.base_url + url,
                    'url': environ_config.UI_URLS.get('product') + separate_uid_from_url(url)
                }
                related.append(pro)

        self.product['related'] = related

    # async def parse_amazon(self, response):
    #     soup = BeautifulSoup(response.content, "html.parser")
    #     dom = etree.HTML(str(soup))
    #     self.product['asin'] = dom.xpath(amazon_tag_identifiers.get('asin'))
    #     amazon_price = dom.xpath(amazon_tag_identifiers.get('price'))[0].text
    #     delivery_status = 'Delivery charges applicable as per Amazons policy.'
    #     price = {
    #         'shop': 'Amazon',
    #         'price': process_integer_from_string(amazon_price),
    #         'delivery': delivery_status,
    #         'source': self.amazon_url + self.product['asin']
    #     }
    #     self.product.get('offers').append(price)
