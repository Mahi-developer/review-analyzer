import requests
from bs4 import BeautifulSoup
from lxml import etree
from sanic.log import logger
from app.utils.utils import process_integer_from_string, preprocess_review

review_tag_identifier = "//div[@class='Rw0r3e']/div[last()]"
rating_tag_identifier = "//div[@class='Yoga0 DApVsf']/@aria-label"
next_page_tag_identifier = "//a[@class='PNHYKd']/@href"
next_page_tag_identifier_ = "//div[@class='PNHYKd']"
total_review_count_identifier = "//div[@class='vKu5p']"


class ReviewExtractor:

    def __init__(self, uid):
        if not uid:
            logger.warning(f'| {self.__class__.__name__} | uid param was null - it should not be null')
            raise Exception('uid should not be null')
        self.uid = uid
        self.url = f'https://www.google.com/shopping/product/{uid}/reviews?prds=rnum:4'
        self.reviews = []
        self.base_url = 'https://www.google.com'
        self.session = requests.session()
        self.headers = (
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'
            }
        )
        self.count = 1
        self.neutral_count = 0
        self.total_count = 0

    async def extract(self):
        with self.session.get(self.url, headers=self.headers) as response:
            if response.status_code == 200:
                await self.parse(response)
            else:
                return {
                    'status': 'Unable to get product details',
                    'dom': response,
                }
        return {
            'reviews': self.reviews,
            'meta_data': {
                'total_reviews': self.total_count,
                'neutral_reviews': self.neutral_count,
                'is_processed': False,
                'uid': self.uid
            }
        }

    async def parse(self, response):
        logger.info(f'| {self.__class__.__name__} | started parsing the reviews')
        try:
            soup = BeautifulSoup(response.content, "html.parser")
            dom = etree.HTML(str(soup))
            review_obj = dom.xpath(review_tag_identifier)
            rating_obj = dom.xpath(rating_tag_identifier)
            self.total_count += len(review_obj)
            if review_obj:
                for i in range(0, len(review_obj)):
                    rating = rating_obj[i].split(' ')[0]
                    if int(rating) == 3:
                        self.neutral_count += 1
                    else:
                        self.reviews.append(
                            preprocess_review(review_obj[i].text)
                        )
            next_page = None
            if self.count < 1:
                next_page = dom.xpath(next_page_tag_identifier)[0]
            else:
                a = soup.findAll('a', href=True)
                for i in a:
                    if 'reviews?' in i['href']:
                        next_page = i['href']
            total_reviews = dom.xpath(total_review_count_identifier)[0].text.split(' ')[0]
            if process_integer_from_string(total_reviews) > len(self.reviews) and len(self.reviews) < 300:
                if next_page:
                    next_page_url = self.base_url + next_page
                    response = requests.get(url=next_page_url, headers=self.headers)
                    if response.status_code == 200:
                        await self.parse(response)
        except Exception as e:
            logger.error(f'| {self.__class__.__name__} | {e.__str__()}')