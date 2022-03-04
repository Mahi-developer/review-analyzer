
class Config:
    ANALYZER_URL = 'http://localhost:8005/analyze'
    UI_URLS = {
        'base': 'http://localhost:8006/',
        'product': 'http://localhost:8006/product/',
        'search': 'http://localhost:8006/search/'
    }


environ_config = Config()
