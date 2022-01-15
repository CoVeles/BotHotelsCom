from decouple import config
from datetime import timedelta
import requests
from constants import LANGUAGE_FOR_REQUEST, CURRENCY
from botrequests.parsing import parse_hotel_info
from loguru import logger

X_RAPIDAPI_KEY = config('RAPIDAPI_KEY')


def get_hotels(req_params: dict, user_id: int,
               lang_id: int) -> list:
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {
        "destinationId": req_params['loc_id'],
        "pageNumber": "1",
        "pageSize": str(req_params['hotels_amount']),
        "checkIn": req_params['check_in'],
        "checkOut": req_params['check_in'] + timedelta(req_params['days']),
        "adults1": "1",
        "sortOrder": "DISTANCE_FROM_LANDMARK",
        "locale": f"{LANGUAGE_FOR_REQUEST[lang_id]}",
        "currency": f"{CURRENCY[lang_id]}"}
    if req_params['price_min'] > 0:
        querystring['priceMin'] = str(req_params['price_min'])
    if req_params['price_max'] > 0:
        querystring['priceMax'] = str(req_params['price_max'])

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': X_RAPIDAPI_KEY
    }
    hotels = []
    try:
        response = requests.request("GET", url, headers=headers,
                                    params=querystring)
        data = response.json()
        results = data['data']['body']['searchResults']['results']
        if len(results) > 0:
            results = [result for result in results
                       if (result['landmarks'][0]['distance']
                           <= req_params['distance'])]
            for result in results:
                try:
                    hotel = parse_hotel_info(result, user_id,
                                             req_params, lang_id)
                    hotels.append(hotel)
                except Exception as e:
                    logger.error(f'{user_id} parsing hotel info err - {e}')
    except requests.exceptions.RequestException as e:
        logger.error(f'{user_id}: req_err - {e}')
    except Exception as e:
        logger.error(f'{user_id} {e}')
    return hotels

