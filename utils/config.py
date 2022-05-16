
class Config:
    ANALYZER_URL = 'http://172.105.49.246:8080/analyze'
    UI_URLS = {
        'base': 'http://localhost:8006/',
        'product': 'http://localhost:8006/product/',
        'search': 'http://localhost:8006/search/'
    }


environ_config = Config()
