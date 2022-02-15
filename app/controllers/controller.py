from sanic import response, Blueprint
from sanic.log import logger
from app.services.analyzer_service import Analyzer
from app.utils.responses import responses
import asyncio

bp_controller = Blueprint('controller')


@bp_controller.route('/', methods=['POST', 'GET'])
async def index_route(request):
    return response.text('This is index url')


@bp_controller.route('/test', methods=['POST', 'GET'])
async def test_configs(request):
    asyncio.run_coroutine_threadsafe(config_test1(), asyncio.get_running_loop())
    return response.text('Returning text without waiting for the previous async method to complete ')


async def config_test1():
    await asyncio.sleep(30)
    logger.info("Done ")


@bp_controller.route('/analyze', methods=['POST', 'GET'])
async def analyze_reviews(request):

    request_json = request.json
    meta_data = request_json.get('meta-data')
    reviews = request_json.get('reviews')
    analyzer_obj = Analyzer(reviews, meta_data)

    try:
        is_processing = asyncio.run_coroutine_threadsafe(
            analyzer_obj.analyze(),
            asyncio.get_running_loop()
        )

    except Exception as e:
        resp = responses.get(400)
        resp.__setitem__('message', resp.get('message') + e.__str__())
        return response.json(resp)

    if is_processing:
        return response.json(responses.get(200))
    return response.json(responses.get(401))
