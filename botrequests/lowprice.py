from decouple import config
from datetime import timedelta
from botrequests.pictures import get_pics_urls
import requests
from constants import PHRASES
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
        "sortOrder": "PRICE",
        "locale": "en_US",
        "currency": "USD"}

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
    finally:
        return hotels


def parse_hotel_info(result: dict, user_id: int,
                     req_params: dict, lang_id: int) -> any:
    try:
        hotel = dict()
        hotel['text'] = ''

        name = result.get('name')
        hotel['text'] += f"{PHRASES['Hotel'][lang_id]}: {name}\n"

        if result['address'].get('streetAddress'):
            address = result['address']['streetAddress']
        else:
            address = result['address'].get('locality')
        hotel['text'] += f"{PHRASES['Address'][lang_id]}: {address}\n"

        distance = result['landmarks'][0].get('distance')
        hotel['text'] += f"{PHRASES['Distance'][lang_id]}: {distance}\n"

        url = f"https://ru.hotels.com/ho{result['id']}"
        hotel['text'] += f"{PHRASES['URL'][lang_id]}: {url}\n"

        price = result['ratePlan']['price'].get('current')
        hotel['text'] += f"{PHRASES['Price'][lang_id]}: {price}\n"

        tot_price = result['ratePlan']['price'].get('exactCurrent')
        tot_price *= req_params['days']
        hotel['text'] += f"{PHRASES['Tot_price'][lang_id]}: " \
                         f"{tot_price} {PHRASES['Curr'][lang_id]}"

        if req_params['pictures'] > 0:
            try:
                hotel['pictures']: list = get_pics_urls(
                    result['id'], req_params['pictures']
                )
            except Exception as e:
                logger.error(f"{user_id} pictures url getting err: "
                             f"hotel id {result['id']} - {e}")
    except Exception as e:
        raise Exception(f"hotel id {result['id']} - {e}")

    return hotel
