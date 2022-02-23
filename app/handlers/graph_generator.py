import matplotlib.pyplot as plt
import numpy as np
from sanic.log import logger
from wordcloud import WordCloud, STOPWORDS


class WordClouds:

    def __init__(self, reviews, asin):
        self.reviews = reviews
        self.files = ['word_cloud.png']

    async def generate_word_cloud(self):
        try:
            cloud_text = " ".join(review for review in self.reviews)
            stopwords = set(STOPWORDS)
            word_cloud = WordCloud(
                width=800,
                height=600,
                margin=2,
                max_font_size=50,
                background_color='white',
                min_font_size=10,
                stopwords=stopwords
            ).generate(cloud_text)
            plt.imshow(word_cloud, interpolation='bilinear')
            plt.axis('off')
            plt.savefig(self.files[0], format='png')
            plt.clf()

            logger.info('word cloud generated and saved in location: /word_cloud.png')
        except Exception as e:
            logger.error('Unexpected exception occurred while generating word cloud-- \n' + e.__str__())
            pass


class Plotter:

    def __init__(self, label, meta_data):
        self.label = label
        self.meta_data = meta_data
        self.asin = meta_data.get('uid')
        self.files = [
            'reviews_pie_chart.png',
            'ratings_bar_graph.png',
            'price_graph.png'
        ]

    async def find_explode_for_max(self, y):
        max_ = max(y)
        if max_ == (self.label == 1).sum():
            return [0.1, 0, 0]
        elif max_ == (self.label == 0).sum():
            return [0, 0.1, 0]
        else:
            return [0, 0, 0.1]

    async def plot_analysis_result(self):
        positive = (self.label == 1).sum()
        negative = (self.label == 0).sum()
        neutral = self.meta_data.get('ratings_breakdown').get('three_stars')

        await self.plot_pie_chart_reviews(positive, negative, neutral)
        await self.plot_bar_graph_for_ratings()
        await self.plot_price_graph()

    async def plot_pie_chart_reviews(self, positive, negative, neutral):
        """
            :parameter: positive, negative, neutral review counts
            :returns: None
            :desc: saves reviews pie chart
        """
        try:
            y = np.array([positive, negative, neutral])
            explodes = await self.find_explode_for_max(y)

            # change design label as per our convenience
            labels = ['positive - ' + str(positive), 'negative - ' + str(negative), 'neutral - ' + str(neutral)]
            colors = ['#008000', '#9e0000', '#356bb0']  # change respective pie chart colors here
            plt.pie(
                y,
                explode=explodes,
                labels=labels,
                shadow=True,
                colors=colors
            )
            plt.savefig(
                self.files[0],
                format='png'
            )
            plt.clf()
            logger.info('reviews pie chart generated and saved in location: /reviews_pie_chart.png')
        except Exception as e:
            logger.error(
                'Unexpected exception occurred while generating pie chart for reviews-- \n' +
                e.__str__()
            )
            pass

    async def plot_bar_graph_for_ratings(self):
        """
            :parameter: meta_data to get ratings breakdown and based on breakdown will plot pie-chart
            :returns: None
            :desc: saves ratings breakdown bar graph
        """
        try:
            ratings_breakdown = self.meta_data.get('ratings_breakdown')
            x = [
                ratings_breakdown.get('five_stars'),
                ratings_breakdown.get('four_stars'),
                ratings_breakdown.get('three_stars'),
                ratings_breakdown.get('two_stars'),
                ratings_breakdown.get('one_star')
            ]
            y = ['one', 'two', 'three', 'four', 'five']
            plt.barh(y, x)
            plt.ylabel('Ratings breakdown')
            plt.savefig(self.files[1], format='png')
            plt.clf()
            logger.info('ratings bar graph generated and saved in location: /ratings_bar_graph.png')
        except Exception as e:
            logger.error(
                'Unexpected exception occurred while generating bar graph for ratings break down -- \n' +
                e.__str__()
            )
            pass

    async def plot_price_graph(self):
        """
            :parameter: meta_data to get price and based on price will plot a bar graph
            :returns: None
            :desc: saves ratings price bar graph
        """
        try:
            price = self.meta_data.get('price')
            x = [
                'Amazon',
                'Flipkart',
                'Ebay',
                'Myntra'
            ]
            y = [
                price.get('amazon'),
                price.get('flipkart'),
                price.get('ebay'),
                price.get('myntra')
            ]
            plt.bar(x, y, color="#4CAF50", width=0.3)
            min_ = min(y) - (max(y) - min(y))
            max_ = max(y) + (max(y) - min(y))
            plt.ylim(min_, max_)
            plt.savefig(self.files[2], format='png')
            plt.clf()
            logger.info('price comparison bar graph generated and saved in location: /price_graph.png')
        except Exception as e:
            logger.error(
                'Unexpected exception occurred while generating bar graph for price -- \n' +
                e.__str__()
            )
            pass
