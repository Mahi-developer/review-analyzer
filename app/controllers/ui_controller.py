import asyncio

from sanic import response, Blueprint
from app.services.firebase_service import FirebaseService
from app.scrapper import extract_handler

ui_controller = Blueprint('ui_controller')


@ui_controller.route('/product/<uid>', methods=['POST', 'GET'])
async def index_route(request, uid):
    firebase = FirebaseService(uid)
    resp = await firebase.get_product(uid)
    if not resp:
        resp = await extract_handler.extract_product_data(uid)
        await firebase.save(resp)
    if not resp.get('is_analysis_done'):
        asyncio.run_coroutine_threadsafe(
            extract_handler.extract_reviews_data(uid),
            asyncio.get_running_loop()
        )

    return response.json(resp)
