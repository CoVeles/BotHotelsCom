from botrequests.pictures import get_pics_urls
from constants import PHRASES
from loguru import logger


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
