from decouple import config
import requests

X_RAPIDAPI_KEY = config('RAPIDAPI_KEY')


def get_pics_urls(hotel_id: str, number_of_pics: int):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': X_RAPIDAPI_KEY
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
    except requests.exceptions.RequestException as e:
        return [f'Server error: {e}']
    data = response.json()
    try:
        pics: list = [pic_url['baseUrl'].replace('{size}', 'b')
                      for pic_url in data['hotelImages'][:number_of_pics]]
    except Exception as e:
        return [f'Pictures parsing error: {e}']
    return pics

