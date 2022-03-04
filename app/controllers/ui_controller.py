import asyncio
from urllib.parse import unquote_plus
from sanic import response, Blueprint
from app.services.firebase_service import FirebaseService
from app.scrapper import extract_handler
from app.utils.responses import responses

ui_controller = Blueprint('ui_controller')


@ui_controller.route('/product/<uid>', methods=['POST', 'GET'])
async def product(request, uid):
    firebase = FirebaseService(uid)
    resp = await firebase.get_product(uid)
    if not resp:
        resp = await extract_handler.extract_product_data(uid)
        if resp:
            if not resp.get('is_analysis_done'):
                asyncio.run_coroutine_threadsafe(
                    extract_handler.extract_reviews_data(uid),
                    asyncio.get_running_loop()
                )
            await firebase.save(resp)
            return response.json(resp)

    return response.json(responses.get(402))


@ui_controller.route('/search/<search_term>', methods=['POST', 'GET'])
async def search(request, search_term):
    search_query = unquote_plus(search_term)
    resp = await extract_handler.extract_search_data(search_query)
    return response.json(resp)
