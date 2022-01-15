from decouple import config
import requests
import re
from constants import LANGUAGE_FOR_REQUEST, CURRENCY
from loguru import logger

X_RAPIDAPI_KEY = config('RAPIDAPI_KEY')


class ParsingLocError(Exception):
    pass


class ParsingLocNull(Exception):
    pass


def get_locations_from_api(loc_name: str, lang_id: int,
                           user_id: int) -> dict:
    url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
    querystring = {'query': loc_name,
                   'locale': LANGUAGE_FOR_REQUEST[lang_id],
                   'currency': CURRENCY[lang_id]}
    headers = {
        'x-rapidapi-host': 'hotels4.p.rapidapi.com',
        'x-rapidapi-key': X_RAPIDAPI_KEY
    }
    logger.info(f'Attempt to request locations from API')
    locations = {}
    try:
        response = requests.request('GET', url, headers=headers,
                                    params=querystring, timeout=20)
        data = response.json()
        if data.get('message'):
            raise requests.exceptions.RequestException

        locations: dict = parse_locations(data)

    except requests.exceptions.RequestException as e:
        logger.error(f'{user_id}: req_err - {e}')
    except ParsingLocError:
        logger.error(f'{user_id}: parsing locations err')
    except ParsingLocNull:
        logger.error(f'{user_id}: locations not found')
    except Exception as e:
        logger.error(f'{user_id}: locations err - {e}')
    return locations


def parse_locations(data: requests) -> dict:
    try:
        locations = dict()
        if len(data.get('suggestions')[0].get('entities')) > 0:
            for item in data.get('suggestions')[0].get('entities'):

                location_name = re.sub('<([^<>]*)>', '', item['caption'])
                locations[item['destinationId']] = (location_name,
                                                    location_name)
            return locations
        else:
            raise ParsingLocNull
    except ParsingLocNull:
        raise ParsingLocNull
    except Exception:
        raise ParsingLocError
