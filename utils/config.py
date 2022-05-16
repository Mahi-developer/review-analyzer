
class Config:
    ANALYZER_URL = 'http://45.79.125.92:8080/analyze'
    UI_URLS = {
        'base': 'http://localhost:8006/',
        'product': 'http://localhost:8006/product/',
        'search': 'http://localhost:8006/search/'
    }


environ_config = Config()
