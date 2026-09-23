import requests
import sys


def get_owned_games(steam_id, steam_api_key, include_appinfo=False, include_played_free_games=False):
    """
    A function that requests a list of all owned games for a steam id.
    :param steam_id: The SteamID of the account.
    :type steam_id: int
    :param include_appinfo: Include game name and logo information in the output. The default is to return appids only.
    :type include_appinfo: bool
    :param include_played_free_games: By default, free games like Team Fortress 2 are excluded (as technically everyone
    owns them). If include_played_free_games is set, they will be returned if the player has played them at some
    point. This is the same behavior as the games list on the Steam Community.
    :type include_played_free_games: bool
    :return: The total number of games the user owns (including free games they've played, if include_played_free_games
    was passed), Plus A games array, with the following contents (note that if "include_appinfo" was not passed in the
    request, only appid, playtime_2weeks, and playtime_forever will be returned):
    appid - Unique identifier for the game
    name - The name of the game
    playtime_2weeks - The total number of minutes played in the last 2 weeks
    playtime_forever - The total number of minutes played "on record", since Steam began tracking total playtime in
    early 2009.
    img_icon_url, img_logo_url - these are the filenames of various images for the game. To construct the URL to the
    image, use this format: http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{hash}.jpg. For
    example, the TF2 logo is returned as "07385eb55b5ba974aebbe74d3c99626bda7920b8", which maps to the URL: [1]
    has_community_visible_stats - indicates there is a stats page with achievements or other game stats available for
    this game. The uniform URL for accessing this data is http://steamcommunity.com/profiles/{steamid}/stats/{appid}.
    For example, Robin's TF2 stats can be found at: http://steamcommunity.com/profiles/76561197960435530/stats/440.
    You may notice that clicking this link will actually redirect to a vanity URL like /id/robinwalker/stats/TF2
    :rtype: tuple[int, dict]
    """
    request = (f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
               f"?key={steam_api_key}"
               f"&steamid={steam_id}"
               f"&format=json")
    if include_appinfo:
        request += "&include_appinfo=True"
    if include_played_free_games:
        request += "&include_played_free_games=True"
    response = requests.get(request, timeout=15)
    data = response.json()['response']
    return data['game_count'], data['games']


def get_steam_game_icon(game_id, icon_hash):
    icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{game_id}/{icon_hash}.jpg"
    icon = requests.get(icon_url, timeout=15).content
    return icon


def get_steam_banner(game_id):
    banner_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{game_id}/library_600x900_2x.jpg"
    banner = requests.get(banner_url, timeout=15).content
    return banner


def get_steam_info(game_id):
    info_url = f"https://store.steampowered.com/api/appdetails?appids={game_id}"
    game_data = requests.get(info_url, timeout=15).json()[str(game_id)]
    if not game_data['success']:
        return ""
    game_info = game_data["data"]["short_description"]
    return game_info
