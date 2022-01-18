import requests
from decouple import config

X_RAPIDAPI_KEY = config('RAPIDAPI_KEY')


def get_pics_urls(hotel_id: str, number_of_pics: int) -> list:
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': X_RAPIDAPI_KEY
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
    except requests.exceptions.RequestException as e:
        raise Exception(f'req_err: {e}')
    try:
        data = response.json()
        pics: list = [pic_url['baseUrl'].replace('{size}', 'b')
                      for pic_url in data['hotelImages'][:number_of_pics]]
    except Exception as e:
        raise Exception(f'Pictures parsing error: {e}')
    return pics

