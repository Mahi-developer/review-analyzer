import requests

from datetime import datetime
from sanic.log import logger
from app.services.firebase_service import FirebaseService
from app.utils.utils import preprocess_reviews
from utils.config import environ_config


class Analyzer:

    def __init__(self, reviews, meta_data):
        if not meta_data.get('is_preprocessed'):
            self.reviews = preprocess_reviews(reviews)
        self.meta_data = meta_data
        self.uid = meta_data.get('uid')
        self.created_dtm = None
        self.updated_dtm = None
        self.firebase_service = FirebaseService(self.uid)

    async def analyze(self):
        try:
            if self.reviews and len(self.reviews) != 0:
                logger.info(f"started processing reviews for request")
                await self.predict()
                return True
            error = f" Not able to start process this request in analyze"
            logger.warning(error)
            return False

        except Exception as e:
            error = f"| {self.__class__.__name__} | {e.__str__()} for this request in analyze"
            logger.error(error)

    async def predict(self):
        try:
            # Todo analyze review from the unique api endpoint
            self.created_dtm = datetime.now().strftime('%d-%m-%y %H:%M:%S')
            json = self.process_req()
            resp = await self.generate_response(json)
            await self.firebase_service.update(resp)

        except Exception as e:
            error = f"| {self.__class__.__name__} | {e.__str__()} Unexpected exception caught while prediction"
            logger.error(error)

    # Todo need to change the response accordingly
    async def generate_response(self, prediction: dict):
        try:
            return {
                'meta-data': {
                    'created_dtm': self.created_dtm,
                    'updated_dtm': datetime.now().strftime('%d-%m-%y %H:%M:%S'),
                    'call_back': False
                },
                'analysis': prediction,
            }

        except Exception as e:
            error = f"| {self.__class__.__name__} | {e.__str__()} Unexpected exception caught while generating response"
            logger.error(error)

    def process_req(self):
        json_data = {
            'reviews': self.reviews
        }
        response = requests.post(
            url=environ_config.ANALYZER_URL,
            json=json_data
        )
        logger.info(f'| {self.__class__.__name__} | {response.text}')
        return response.json()
