from bs4 import BeautifulSoup
import httpx
import requests
import urllib.parse
from .utils import TIMEOUT, request

CITY_ADDRESS = "https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8_%D1%81_%D0%BD%D0%B0%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5%D0%BC_%D0%B1%D0%BE%D0%BB%D0%B5%D0%B5_100_%D1%82%D1%8B%D1%81%D1%8F%D1%87_%D0%B6%D0%B8%D1%82%D0%B5%D0%BB%D0%B5%D0%B9"
#CITY_ADDRESS = "https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_Russia_by_population"

def get_top100_cities():
    response = requests.get(CITY_ADDRESS)
    return response.content


#async def get_top100_cities():
#    async with httpx.Client(timeout=TIMEOUT) as client:
#        response = await request(client, CITY_ADDRESS)
#        return response.content
        