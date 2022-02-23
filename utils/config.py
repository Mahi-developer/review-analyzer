# url doc
"""
    amazon_search: search term need to be added at the end,
    amazon_product: uid need to be added at the end,
    amazon_reviews: uid need to be replaced and the pageNumber needed to be added at the end
    price_urls: {
        amazon: uid need to be added at the end
        others: search term need to be added at the end of all other urls get ST from amazon product title
    }
    google_shopping: {
        doc: This google shopping can be modified in diff ways...
            * need to add the country_code
            * need to add the google product id
            * need to add the type (ex: (empty for: product), review, offers)
        example-url: https://www.google.com/shopping/product/r/IN/12976475649125200916/reviews
    }
"""

urls = {
    'amazon_search': 'https://www.amazon.in/s?k=',
    'amazon_product': 'https://www.amazon.in/dp/',
    'amazon_reviews': 'https://www.amazon.in/product-reviews/asin?pageNumber=',
    'price_urls': {
        'amazon': 'https://www.amazon.in/dp/',
        'flipkart': '',
        'ebay': '',
        'myntra': 'https://www.myntra.com/'
    },
}

google_shopping = {
    'url': 'https://www.google.com/shopping/product/r/',
    'country': 'IN/',
    'types': {
        'product': '/',
        'review': '/review/',
        'offers': '/offers/',
        'specs': '/specs/'
    }
}

default_config = {

}
