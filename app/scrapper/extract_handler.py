from app.scrapper.product_extractor import ProductExtractor
from app.scrapper.review_extractor import ReviewExtractor
from app.scrapper.search_extractor import SearchExtractor
from app.services.analyzer_service import Analyzer
from sanic.log import logger


async def extract_product_data(uid, url=None):
    pe = ProductExtractor(uid)
    pro = await pe.extract(url)
    if pro and pro.get('uid'):
        return pro
    return None


async def extract_reviews_data(uid):
    re = ReviewExtractor(uid)
    reviews = await re.extract()
    if reviews and reviews.get('reviews'):
        await Analyzer(reviews=reviews.get('reviews'), meta_data=reviews.get('meta_data')).analyze()
    else:
        logger.error(f'| extract_reviews_data | Empty or error response from review extractor | {reviews}')


async def extract_search_data(search_query):
    se = SearchExtractor(search_query)
    return await se.extract()
