from app.scrapper.product_extractor import ProductExtractor
from app.scrapper.review_extractor import ReviewExtractor
from app.services.analyzer_service import Analyzer


async def extract_product_data(uid):
    pe = ProductExtractor(uid)
    return await pe.extract()


async def extract_reviews_data(uid):
    re = ReviewExtractor(uid)
    reviews = await re.extract()
    meta_data = {
        'uid': uid,
        'is_preprocessed': False
    }
    await Analyzer(reviews=reviews, meta_data=meta_data).analyze()