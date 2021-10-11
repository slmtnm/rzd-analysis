import requests
from json import JSONDecodeError
class Utils:
    def __init__(self):
        self.__timetable_address = "https://pass.rzd.ru/timetable/public/ru?"
        self.__acs_express3_address = "https://pass.rzd.ru/suggester?compactMode=y&lang=ru"

    def get_express3id_by_name(self, st_name: str) -> int:
        req = self.__acs_express3_address + f'&stationNamePart={st_name.upper()}'
        response = requests.get(req)
        response.raise_for_status()
        try:
            st_variants = response.json()
        except: # TODO судя по дебаггеру тут JSONDecodeError но нет
            return -1
        station_code = [st["c"] for st in st_variants if st["n"] == st_name.upper()]
        # TODO иногда станции содержат также название ЖД, которой принадлежат.
        # TODO Необходимо обрабатывать такие случаи
        if len(station_code) > 1:
            raise RuntimeError(f"Found {len(station_code)} stations with name {st_name}")
        elif len(station_code) == 0:
            return -1
        return station_code[0]

    def get_rid(self, layer_id, params) -> str:
        req = self.__timetable_address + 'layer_id=' + str(layer_id) + \
              ''.join(['&' + key + '=' + str(params[key]) for key in params.keys()])

        response = requests.get(req)
        response.raise_for_status()
        try:
            response_json = response.json()
        except: # TODO JSONDecodeError
            return '-1'
        if response_json.get("result") != "RID":
            raise RuntimeError("RID request did not return RID")
        return response.json().get("RID")

    def request_by_rid(self, layer_id, rid):
        req = self.__timetable_address + f'layer_id={layer_id}&rid={rid}'
        response = requests.get(req)
        response.raise_for_status()
        try:
            response_json = response.json()
        except:  # TODO JSONDecodeError
            return '-1'
        if response_json.get("result") != "OK":
            raise RuntimeError("Request by rid was failed")
        return response_json
