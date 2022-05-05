import asyncio
import requests

from datetime import datetime
from sanic.log import logger
from bs4 import BeautifulSoup

from app.scrapper import extract_handler
from app.services.firebase_service import FirebaseService
from app.utils.utils import (
    process_integer_from_string,
    separate_uid_from_url,
    separate_shop_name
)


class SearchExtractor:

    def __init__(self, search_query):
        if not search_query:
            raise Exception('Search query is needed!')
        self.base_url = 'https://www.google.com'
        self.url = f'https://www.google.com/search?tbm=shop&q={search_query}'
        self.headers = (
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'
            }
        )
        self.session = requests.session()
        self.products = []
        self.created_dtm = datetime.now()
        self.uid_list = []

    async def extract(self):
        with self.session.get(self.url, headers=self.headers) as response:
            if response.status_code == 200:
                await self.parse_products(response)
                asyncio.run_coroutine_threadsafe(
                    self.parse(),
                    asyncio.get_running_loop()
                )
            else:
                return {
                    'status': 'Unable to get product details',
                    'dom': response,
                }
        return {
            'meta_data': {
                'products_count': len(self.products),
                'status': 'Products extracted successfully',
                'status_code': 200,
                'created_dtm': str(self.created_dtm),
                'extracted_dtm': str(datetime.now()),
                'analysis_status': 'Processing in the background'
            },
            'products': self.products
        }

    async def parse_products(self, response):
        logger.info(f'| {self.__class__.__name__} | started extracting the products data')
        soup = BeautifulSoup(response.content, "html.parser")
        products = soup.findAll('div', class_='xcR77')
        for i in products:
            div = i.find('div', class_='p9MVp')
            if div:
                delivery_span = i.find('span', class_='dD8iuc')
                delivery = None
                if delivery_span:
                    delivery = delivery_span.text
                img_div = i.find('div', class_='oR27Gd')
                uid = separate_uid_from_url(div.find('a')['href'])
                self.uid_list.append(uid)
                shop_div = i.find('div', class_='P8xhZc')
                shop = None
                for div in shop_div.findAll('div'):
                    if '₹' in div.text:
                        shop = div.text
                pro = {
                    'uid': uid,
                    'title': i.find('div', class_='rgHvZc').text,
                    'price': process_integer_from_string(i.find('span', class_='HRLxBb').text),
                    'shop': separate_shop_name(shop),
                    'price_raw': shop,
                    'total_reviews': process_integer_from_string(i.find('div', class_='dD8iuc').text),
                    'delivery': delivery,
                    'img': img_div.find('img')['src']
                }
                self.products.append(pro)

    async def parse(self):
        logger.info(f'| {self.__class__.__name__} | started parsing the product info to store in firebase')
        for uid in self.uid_list:
            product = await extract_handler.extract_product_data(uid=uid)
            firebase = FirebaseService(uid)
            await firebase.save(product)
            if not product.get('is_analysis_done'):
                await extract_handler.extract_reviews_data(uid)
            else:
                logger.warning(f'| {self.__class__.__name__} | Analysis is already available!')


