

responses = {
    200: {
        'status_code': 200,
        'status': 'success',
        'message': 'Processing the reviews will update the analysis soon in firebase'
    },
    400: {
        'status_code': 400,
        'status': 'error',
        'message': 'Unexpected Error while processing the reviews check error logs for more info | '
    },
    404: {
        'status_code': 404,
        'status': 'error',
        'message': 'Page not found, check the endpoint'
    },
    405: {
        'status_code': 405,
        'status': 'error',
        'message': 'Wrong request method see docs for the request method for particular endpoints'
    },
    401: {
        'status_code': 401,
        'status': 'failure',
        'message': 'Not able to process the reviews now, kindly try after sometime!'
    },
    402: {
        'status_code': 402,
        'status': 'failure',
        'message': 'Not able to process the current chosen Product!'
    }
}
