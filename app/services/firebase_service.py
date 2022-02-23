import os.path

import firebase_admin
from firebase_admin import (
    credentials,
    initialize_app,
    firestore,
    storage
)
from sanic.log import logger
import requests


class FirebaseService:

    def __init__(self, uid):
        self.db = None
        self.storage_bucket = None
        self.base_url = 'https://firebasestorage.googleapis.com/v0/b/sentimental-analysis-fproject.appspot.com/o/' \
                        + uid
        self.uid = uid
        self.asin_url = uid + '/'
        self.files = [
            'word_cloud.png',
            'reviews_pie_chart.png',
            'ratings_bar_graph.png',
            'price_graph.png'
        ]
        try:
            firebase_admin.get_app()
        except ValueError:
            self.connect()

    def get_base_public_url(self):
        return self.base_url

    def connect(self):
        try:
            try:
                firebase_admin.get_app()
            except ValueError:
                credential = credentials.Certificate('utils/firebase-adminsdk-certificate.json')
                initialize_app(
                    credential=credential,
                    options={
                        'storageBucket': 'sentimental-analysis-fproject.appspot.com'
                    }
                )
                logger.info('Connected successfully!')
            self.db = firestore.client()
            self.storage_bucket = storage.bucket()
        except Exception as e:
            logger.error(
                'Unexpected exception occurred while connecting with firebase -- \n' +
                e.__str__()
            )
            raise Exception('Firebase Connection Error | ' + e.__str__())

    async def check_is_existing(self):
        try:
            if self.storage_bucket:
                blob = self.storage_bucket.blob(self.asin_url + self.files[0])
            else:
                self.connect()
                blob = self.storage_bucket.blob(self.asin_url + self.files[0])
            req = requests.head(blob.public_url)
            if req.status_code in [requests.codes.ok, 200]:
                logger.info('')
                return True

        except Exception as e:
            logger.error(
                'Unexpected exception occurred while checking for existing files in firebase | \n' +
                e.__str__()
            )
            raise Exception('Firebase connection error while checking for existing files | ' + e.__str__())
        return False

    async def generate_public_urls(self):
        try:
            urls = []
            for file in self.files:
                if self.storage_bucket:
                    blob = self.storage_bucket.blob(self.asin_url + file)
                else:
                    self.connect()
                    blob = self.storage_bucket.blob(self.asin_url + file)
                urls.append(blob.public_url)
            return urls
        except Exception as e:
            logger.error(
                'Unexpected exception occurred while generating url files in firebase | \n' +
                e.__str__()
            )
            raise Exception('Firebase connection error generating url files in firebase | ' + e.__str__())

    async def update(self, analysis):
        try:
            if self.db:
                doc_ref = self.db.collection(u'products').document(self.uid)
            else:
                self.connect()
                doc_ref = self.db.collection(u'products').document(self.uid)
            doc_ref.update(
                {
                    u'analysis': analysis,
                    u'is_analysis_done': True
                }
            )
            await self.clean_reviews_json_file()
            logger.info('Analysis updated in firestore successfully!')
        except Exception as e:
            logger.error(
                'Unexpected exception occurred while updating analysis in firestore -- \n' +
                e.__str__()
            )
            raise Exception('Unexpected exception occurred while updating analysis in firestore | ' + e.__str__())

    async def save(self, product):
        try:
            if self.db:
                doc_ref = self.db.collection(u'products').document(self.uid)
            else:
                self.connect()
                doc_ref = self.db.collection(u'products').document(self.uid)
            doc_ref.set(product)
            logger.info('Product saved in firestore successfully!')
        except Exception as e:
            logger.error(
                'Unexpected exception occurred while saving product in firestore -- \n' +
                e.__str__()
            )
            raise Exception('Unexpected exception occurred while saving product in firestore | ' + e.__str__())

    async def upload_wc_to_bucket(self):
        try:
            if self.storage_bucket:
                blob = self.storage_bucket.blob(self.asin_url + self.files[0])
            else:
                self.connect()
                blob = self.storage_bucket.blob(self.asin_url + self.files[0])
            blob.upload_from_filename(filename=self.files[0])
            logger.info('Word cloud uploaded successfully!')
        except Exception as e:
            logger.error(
                'Unexpected exception occurred while uploading word cloud -- \n' +
                e.__str__()
            )
            raise Exception('Unexpected exception occurred while uploading word cloud | ' + e.__str__())

    async def upload_gps_to_bucket(self):
        try:
            if self.storage_bucket:
                reviews_chart = self.storage_bucket.blob(self.asin_url + self.files[1])
            else:
                self.connect()
                reviews_chart = self.storage_bucket.blob(self.asin_url + self.files[1])
            reviews_chart.upload_from_filename(filename=self.files[1])
            logger.info('Reviews pie chart uploaded successfully!')

            ratings_chart = self.storage_bucket.blob(self.asin_url + self.files[2])
            ratings_chart.upload_from_filename(filename=self.files[2])
            logger.info('Ratings pie chart uploaded successfully!')

            price_graph = self.storage_bucket.blob(self.asin_url + self.files[3])
            price_graph.upload_from_filename(filename=self.files[3])
            logger.info('Price bar graph uploaded successfully!')
        except Exception as e:
            logger.error(
                'Unexpected exception occurred while uploading graph plot images -- \n' +
                e.__str__()
            )
            raise Exception('Unexpected exception occurred while uploading graph plot images | ' + e.__str__())

    @staticmethod
    async def clean_reviews_json_file():
        if os.path.exists('reviews.json'):
            os.remove('reviews.json')
        else:
            logger.warning('| firebase | no file found reviews.json')
