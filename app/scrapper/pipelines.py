import asyncio
import json
from app.services.firebase_service import FirebaseService
from app.services.analyzer_service import Analyzer
from sanic.log import logger


class ProductPipeline:

    def __init__(self):
        self.uid = None
        self.firebase_service = None

    def process_item(self, item, spider):
        self.uid = item.get('uid')
        self.firebase_service = FirebaseService(self.uid)
        if item:
            try:
                asyncio.run(self.firebase_service.save(item))
            except Exception as e:
                logger.error('| pipeline | Unexpected error occurred while saving product to firebase | ' + e.__str__())
                pass
        else:
            logger.warning('| pipeline | No product is fetched from spider | item param was null')
        return item


class ReviewPipeline:

    def __init__(self):
        self.analyzer = None

    def process_item(self, item, spider):
        if item:
            try:
                json_obj = json.dumps(item, indent=4)
                with open('reviews.json', 'w') as out:
                    out.write(json_obj)
                self.analyzer = Analyzer(
                    meta_data=item.get('meta-data'),
                    reviews=item.get('reviews')
                )
                asyncio.run(
                    self.analyzer.analyze()
                )
            except Exception as e:
                logger.error('| pipeline | Unexpected error occurred while processing reviews | ' + e.__str__())
                pass
        else:
            logger.warning('| pipeline | No reviews from spider | item param was null')
        return item

