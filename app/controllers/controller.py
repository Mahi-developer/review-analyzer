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


"""
sample analyze request

{
    "meta-data":{
        "asin":"B086KCCKKW",
        "total_reviews": 10,
        "is_preprocessed":false,
        "ratings_breakdown":{
            "five_stars":4,
            "four_stars":2,
            "three_stars":1,
            "two_stars":1,
            "one_star":2
        },
        "is_update":true,
        "price":{
            "amazon":50499,
            "flipkart":51000,
            "ebay":53000,
            "myntra":51500
        }
    },
    "reviews": ["Fast transferring data, working nicely but all interested person can't buy due to high price. Recommended for buy.",
    "The item I've received is a fake one. After seeing the package, I doubt the item right away, the packaging & the colour of the item looks very fake to me. So, I open the package carefully, and test it right away; my doubt was confirmed, it was a fake one. I don't want to give any stars, but I system demand at least one, so I'm giving 1","Good memory card , got proper space",
    "Product as described. Note that this is has a UHS speed class of 1. If you want to shoot 4k, you're better off looking for a speed class of 3",
    "Hi Team, I am writing to you for this product..I now its quite a time i purchased this but somehow the SD card i got is now not running properly and is showing as corrupted in my phone..I know there is a warranty/guarantee attached to this but its been only 2 months and the card is not working. Can you please replace it with it a new one? Thanks ! Ritesh.",
    "Be very carefully. They send me fake/copy sd card. It not genuine sandisk. Orginal is same price and come with 10year warranty. Called sandisk customer care when i was having issues.",
    "I buy products based on customers honest purchased reviews, unfortunately they have clubbed all the size capacity mmc reviews together... I.e. 9000+ Why not individual reviews! Anyway... Checked with fakeflashtest.exe and verified the storage capacity of the 400gb mmc, out of the box usage is 366gb n not 400gb as with all the other cards which use some percentage of storage for system files... Out of the box transferred 260 gb data (mp3, movies, photo, software and mix) continuously, too around 1 to 1.3 hrs or so @ 35-50 mb p sec , not as claimed. Probably on the phone it is possible. Hope it lasts at least 5 yrs for my money invested, never go for Samsung mmc cards as tether conk off in a few months for phone usage, issues with apps too after removing from the phones. Had this experience for 3 Samsung mmc. Been using Strontium for 7 yrs without any issues n have 5 cards. Unfortunately they don't come over 128gb capacity so had to opt for SanDisk 400gb on my Galaxy Note 9.. 512gb is just way too expensive. But this one is 1700cheaper now, bought one 10 days back at 7800 Screw you'll.. Edit.. bty mine is still working fine after a year with a room of software an movies n songs n what not.. I myself don't know where... Probably nowadays they sell fake suff MMC like ebay India site used to do n shut down... Not so far long for Amazon. In if no quality testing is done before !",
    "This review is not for sandisk memory card this is for seller J P W Mobile Accessories. I ordered for 128 gb memory card and he send me fake memory card of his name I.e J P W memory card as you can seen in the pictures & replaced memory card which I received that too was fake sandisk memory card as there is misprint in logo and NO MRP, PACKAGING DATE etc was printed on the back. Beware of this seller.",
    "I received this product on time but the product's packaging came bent on one side(The bent was just nearer to the memory card) and it looks like it was made to place it on the bubble wrap. I don't know if the seller (Suvidha Mobile) really knew the value of a memory card or how it works - they just bent the package containing a 1mm thick memory chip to fit on a bubble wrap!! Amazon need to teach them how not to handle a delicate electronic hardware. But, thankfully the memory card din't suffered any damage (I think so!!) and also it working well till now I am using this memory card on my Sony Xperia M C1904.running Custom ROM. It is working perfect and Yes, due to class A1, I'm noticing some speed improvements on apps stored on SD Card (Remember Android Marshmallow and above versions only supports apps on SD card - My Phone provider gave me only Android Jellybean- I installed Custom ROM which currently has Android Nougat v7.1.2) Also this one doesn't comes with microSD to SD adapter {Link for the one with adapter - Cheaper than this one -SanDisk Ultra A1 16GB Class 10 Ultra microSD UHS-I Card with Adapter (SDSQUAR-016G-GN6MA) } So if you are using android marshmallow and above, you can use this memory card for increased app performance for apps stored in microSD card, else go for normal class 10 Cards..",
    "The memory card was delivered on time the write and read speeds are as expected using it in my mobile and works completely as expected.This is a nice product! Works completely fine"
    ]
}
"""