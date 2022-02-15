import os
import tensorflow as tf
import re
from os import path
from datetime import datetime
from sanic.log import logger
from transformers import (
    TFDistilBertForSequenceClassification,
    DistilBertTokenizerFast
)
from app.utils.exceptions import exceptions
from app.services.firebase_service import FirebaseService
from app.handlers.graph_generator import (
    WordClouds,
    Plotter
)

loaded_model = TFDistilBertForSequenceClassification.from_pretrained("sentiment")
tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')


class Analyzer:

    def __init__(self, reviews, meta_data):
        self.reviews = reviews
        self.meta_data = meta_data
        self.asin = meta_data.get('asin')
        self.label = None
        self.created_dtm = None
        self.updated_dtm = None
        self.firebase_service = FirebaseService(self.asin)
        self.files = [
            'word_cloud.png',
            'reviews_pie_chart.png',
            'ratings_bar_graph.png',
            'price_graph.png'
        ]

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

            tf_batch = tokenizer(self.reviews, max_length=256, padding=True, truncation=True, return_tensors='tf')
            tf_outputs = loaded_model(tf_batch)
            tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
            label = tf.argmax(tf_predictions, axis=1)

            self.created_dtm = datetime.now().strftime('%d-%m-%y %H:%M:%S')
            label = label.numpy()
            self.label = label

            is_existing = await self.firebase_service.check_is_existing()

            if not is_existing or self.meta_data.get('is_update'):
                await WordClouds(self.reviews, self.asin).generate_word_cloud()
                await self.firebase_service.upload_wc_to_bucket()

                await Plotter(self.label, self.meta_data).plot_analysis_result()
                await self.firebase_service.upload_gps_to_bucket()

                response = await self.generate_response()
                await self.firebase_service.save(response)

                await self.clean_up_local_files()
                logger.info(response)
            else:
                logger.warning('Analysis Result already present in firebase for this asin: ' + self.asin)

        except Exception as e:
            error = f"{e.__str__()} Unexpected exception caught for this request"
            logger.error(error)
            raise exceptions.get('analyzer').__new__(self, e, error)

    async def generate_response(self):
        try:
            total_reviews = len(self.reviews)
            positive_reviews = (self.label == 1).sum()
            negative_reviews = (self.label == 0).sum()
            neutral_reviews = self.meta_data.get('ratings_breakdown').get('three_stars')
            positive_percent = (positive_reviews / total_reviews) * 100
            negative_percent = (negative_reviews / total_reviews) * 100

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
                    'positive_percent': str(positive_percent) + '%',
                    'negative_percent': str(negative_percent) + '%',
                    'base_url': await self.firebase_service.generate_public_urls(),
                }
            }

        except Exception as e:
            error = f"{e.__str__()} Unexpected exception caught for this request"
            logger.error(error)
            raise exceptions.get('analyzer').__new__(self, e, error)

    def preprocess_reviews(self):
        return [
            re.sub(r'[^a-zA-Z0-9]', ' ', review)
            for review in self.reviews
        ]

    async def clean_up_local_files(self):
        try:
            for file in self.files:
                if path.isfile(file):
                    os.remove(file)
                else:
                    logger.warning('path you provided is not a files')
            logger.info('Successfully removed saved local files')
        except Exception as e:
            error = f"{e.__str__()} Unexpected exception caught while removing files from local"
            logger.error(error)
            raise exceptions.get('analyzer').__new__(self, e, error)

