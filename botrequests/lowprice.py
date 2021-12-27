from decouple import config
from datetime import datetime
from botrequests.pictures import get_pics_urls
import requests

X_RAPIDAPI_KEY = config('RAPIDAPI_KEY')


def get_hotels(req_params: dict):
    date = datetime.now().strftime("%Y-%m-%d")
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {
        "destinationId": req_params['loc_id'],
        "pageNumber": "1",
        "pageSize": str(req_params['hotels_amount']),
        "checkIn": date,
        "checkOut": date,
        "adults1": "1",
        "sortOrder": "PRICE",
        "locale": "en_US",
        "currency": "USD"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': X_RAPIDAPI_KEY
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
    except requests.exceptions.RequestException as e:
        return {'req_err': e}
    except Exception as e:
        return {'err': e}
    data = response.json()
    results = data['data']['body']['searchResults']['results']
    hotels: list = parse_hotels_info(results, int(req_params['pictures']))

    return hotels


def parse_hotels_info(results: list, number_of_pics: int):
    hotels = []
    for result in results:
        hotel = dict()
        try:
            # hotel['id'] = result['id']
            hotel['Hotel:'] = result['name']
            hotel['Address:'] = result['address']['streetAddress']
            hotel['Distance to city center:'] = result['landmarks'][0]['distance']
            hotel['Price:'] = result['ratePlan']['price']['current']
            if number_of_pics > 0:
                hotel['pictures']: list = get_pics_urls(result['id'], number_of_pics)
        except Exception as e:
            hotel['err'] = f'Parsing error: {e}'
        hotels.append(hotel)
    return hotels
