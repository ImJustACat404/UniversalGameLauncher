import json
import sys


RUN_LOCATION = '\\'.join(sys.argv[0].split('\\')[:-1])
USER_DATA_FILE_PATH = RUN_LOCATION + "\\Data\\UData.json"


def _get_udata_file():
    with open(USER_DATA_FILE_PATH, 'r') as udata_file:
        json_object = json.load(udata_file)
    return dict(json_object)


def _set_udata_file(data_dict):
    json_object = json.dumps(data_dict, indent=4)
    with open(USER_DATA_FILE_PATH, 'w') as udata_file:
        udata_file.write(json_object)


def get_steam_id():
    data_dict = _get_udata_file()
    steam_id = data_dict["SteamID"]
    return steam_id


def set_steam_id(steam_id):
    data_dict = _get_udata_file()
    data_dict["SteamID"] = steam_id
    _set_udata_file(data_dict)


def set_steam_api_key(api_key):
    data_dict = _get_udata_file()
    data_dict["SteamApiKey"] = api_key
    _set_udata_file(data_dict)


def get_steam_api_key():
    data_dict = _get_udata_file()
    steam_api_key = data_dict["SteamApiKey"]
    return steam_api_key


def main():
    pass


if __name__ == "__main__":
    main()
