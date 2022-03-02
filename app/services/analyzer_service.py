import re
from datetime import datetime
from sanic.log import logger
from app.utils.exceptions import exceptions
from app.services.firebase_service import FirebaseService
import requests


class Analyzer:

    def __init__(self, reviews, meta_data):
        self.reviews = reviews
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
            error = f"Not able to start processing for this request"
            logger.warning(error)
            return False

        except Exception as e:
            error = f"{e.__str__()} for this request"
            logger.error(error)
            raise exceptions.get('analyzer').__new__(self, e, error)

    async def predict(self):
        try:
            is_preprocessed = self.meta_data.get('is_preprocessed')
            if not is_preprocessed:
                self.reviews = self.preprocess_reviews()

            # Todo analyze review from the unique api endpoint

            # self.created_dtm = datetime.now().strftime('%d-%m-%y %H:%M:%S')
            # dom = self.process_req()
            # dom = await self.generate_response(prediction)
            # await self.firebase_service.update(dom)

        except Exception as e:
            error = f"{e.__str__()} Unexpected exception caught for this request"
            logger.error(error)
            raise exceptions.get('analyzer').__call__(self, e, error)

    async def generate_response(self, prediction: list):
        try:
            total_reviews = len(self.reviews)
            positive_reviews = prediction.count('positive')
            negative_reviews = prediction.count('negative')
            neutral_reviews = prediction.count('neutral')

            return {
                'meta-data': {
                    'created_dtm': self.created_dtm,
                    'updated_dtm': datetime.now().strftime('%d-%m-%y %H:%M:%S'),
                    'call_back': False
                },
                'output': {
                    'total': int(total_reviews),
                    'positive': int(positive_reviews),
                    'negative': int(negative_reviews),
                    'neutral': int(neutral_reviews),
                }
            }

        except Exception as e:
            error = f"{e.__str__()} Unexpected exception caught while generating dom"
            logger.error(error)
            raise exceptions.get('analyzer').__new__(self, e, error)

    def preprocess_reviews(self):
        reviews = [
            re.sub(r'[^a-zA-Z0-9]', ' ', review.replace('\n', '').strip())
            for review in self.reviews
        ]
        out = []
        for review in reviews:
            if len(review) <= 256:
                out.append(review)
        if len(out) > 50:
            return out[0:50]
        return out

    def process_req(self):
        req = 'http://localhost:8005/analyze'
        json_data = {
            'reviews': self.reviews
        }
        response = requests.post(req, json=json_data)
        logger.info('dom | ' + response.text)
        return response.json()
