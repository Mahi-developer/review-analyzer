from sanic import Sanic, response
from app.controllers.controller import bp_controller
from app.controllers.ui_controller import ui_controller
from sanic_cors import CORS, cross_origin

CORS_OPTIONS = {"resources": r'/*', "origins": "*", "methods": ["GET", "POST", "HEAD", "OPTIONS"]}
app = Sanic(name=__name__)
app.blueprint(blueprint=[bp_controller, ui_controller])
CORS(app)

@app.route('/ping')
async def ping_check(request):
    return response.text('Hi there!, This is a ping check you are good to GO!')

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8007,
        debug=False
    )

