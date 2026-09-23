import Objects.Game as Game
import Data.GameDBService as GameDBService
import sys
import os
import shutil
import Steam.APITools as SteamAPI
import Epic.EpicApi as EpicAPI
import Data.UserDataService as UdataUtil


RUN_LOCATION = '\\'.join(sys.argv[0].split('\\')[:-1])


def load_games_from_disk():
    exe_games_data = GameDBService.get_exe_games()
    exe_games = []
    for game_data in exe_games_data:
        game = Game.ExeGame(
            game_data[0],
            game_data[2],
            game_data[3],
            game_data[4],
            game_data[1],
            game_data[5],
            game_data[6]
        )
        exe_games.append(game)
    steam_games_data = GameDBService.get_steam_games()
    steam_games = []
    for game_data in steam_games_data:
        game = Game.SteamGame(
            game_data[1],
            game_data[3],
            game_data[4],
            game_data[5],
            game_data[0],
            game_data[6],
            game_data[2]
        )
        steam_games.append(game)
    epic_games_data = GameDBService.get_epic_games()
    epic_games = []
    for game_data in epic_games_data:
        game = Game.EpicGame(
            game_data[1],
            game_data[2],
            game_data[3],
            game_data[4],
            game_data[0],
            game_data[5]
        )
        epic_games.append(game)
    return sorted(steam_games + exe_games + epic_games, key=lambda i: i.get_name().upper())


def load_new_games(existing_games):
    """Create game objects only for database rows not already shown in the UI."""
    existing_ids = {(game.get_platform(), game.get_id()) for game in existing_games}
    new_games = []

    for row in GameDBService.get_exe_games():
        if ("Other", row[5]) not in existing_ids:
            new_games.append(Game.ExeGame(row[0], row[2], row[3], row[4], row[1], row[5], row[6]))
    for row in GameDBService.get_steam_games():
        if ("Steam", row[0]) not in existing_ids:
            new_games.append(Game.SteamGame(row[1], row[3], row[4], row[5], row[0], row[6], row[2]))
    for row in GameDBService.get_epic_games():
        if ("Epic", row[0]) not in existing_ids:
            new_games.append(Game.EpicGame(row[1], row[2], row[3], row[4], row[0], row[5]))

    return new_games


def add_game(platform, name, icon_path, banner_path, info, game_path):
    new_icon_path = copy_image_to_folder(icon_path, name, platform, "Icon")
    new_banner_path = copy_image_to_folder(banner_path, name, platform, "Banner")
    game_id = GameDBService.add_exe_game(name, game_path, new_icon_path, new_banner_path, info)
    new_game = Game.ExeGame(name, new_icon_path, new_banner_path, "", game_path, game_id, info)
    return new_game


def copy_image_to_folder(img_path, game_name, platform, new_img_name):
    game_name = "".join(i for i in game_name if i not in "\/:*?<>|")
    img_extension = '.' + img_path.split('.')[-1]
    new_img_directory = RUN_LOCATION + f"\\Img\\{platform}\\{game_name}"
    new_img_path = new_img_directory + f"\\{new_img_name}" + img_extension
    if not os.path.exists(new_img_directory):
        os.makedirs(new_img_directory)
    with open(img_path, 'rb') as og_file:
        img_bytes = og_file.read()
    with open(new_img_path, 'wb') as new_file:
        new_file.write(img_bytes)
    return new_img_path


def save_image_to_folder(img_bytes, game_name, platform, new_img_name, img_extension=".jpg"):
    game_name = "".join(i for i in game_name if i not in "\/:*?<>|")
    img_directory = RUN_LOCATION + f"\\Img\\{platform}\\{game_name}"
    img_path = img_directory + f"\\{new_img_name}" + img_extension
    if not os.path.exists(img_directory):
        os.makedirs(img_directory)
    with open(img_path, 'wb') as new_file:
        new_file.write(img_bytes)
    return img_path


def remove_game(game):
    game_name = "".join(i for i in game.get_name() if i not in "\/:*?<>|")
    platform = game.get_platform()
    if platform == "Other":
        platform = 'exe'
        GameDBService.remove_exe_game(game.get_id())
    elif platform == "Steam":
        GameDBService.remove_steam_game(game.get_id())
    shutil.rmtree(RUN_LOCATION + f"\\Img\\{platform}\\{game_name}")


def save_game_notes(games):
    for game in games:
        if game.get_platform() == "Steam":
            GameDBService.update_steam_notes(game.get_id(), game.get_notes())
        elif game.get_platform() == "Other":
            GameDBService.update_exe_notes(game.get_id(), game.get_notes())


def update_steam_db():
    steam_id = UdataUtil.get_steam_id()
    steam_api_key = UdataUtil.get_steam_api_key()
    _, steam_game_list = SteamAPI.get_owned_games(steam_id, steam_api_key, include_appinfo=True, include_played_free_games=True)
    saved_game_id_list = GameDBService.get_steam_game_id_list()
    for game in steam_game_list:
        if game['appid'] not in saved_game_id_list:
            game_id = game['appid']
            name = game['name']
            playtime = game['playtime_forever']
            game_icon_hash = game['img_icon_url']
            icon = SteamAPI.get_steam_game_icon(game_id, game_icon_hash)
            icon_path = save_image_to_folder(icon, name, "Steam", "Icon")
            banner = SteamAPI.get_steam_banner(game_id)
            banner_path = save_image_to_folder(banner, name, "Steam", "Banner")
            game_info = SteamAPI.get_steam_info(game_id)
            GameDBService.add_steam_game(game_id, name, playtime, icon_path, banner_path, game_info)


def update_epic_db():
    owned_epic_game_list = EpicAPI.get_owned_game_list()
    saved_game_id_list = GameDBService.get_epic_game_id_list()
    for game in owned_epic_game_list:
        if game['app_name'] not in saved_game_id_list:
            game_id = game["app_name"]
            name = game["app_title"]
            try:
                banner_url = [x for x in game["metadata"]["keyImages"] if x["type"] == "DieselGameBoxTall"][0]["url"]
            except IndexError:
                banner_url = ""
            banner = EpicAPI.get_epic_banner(banner_url)
            icon = banner
            banner_path = save_image_to_folder(banner, name, "Epic", "Banner")
            icon_path = save_image_to_folder(icon, name, "Epic", "Icon")
            game_info = game["metadata"]["description"]
            GameDBService.add_epic_game(game_id, name, icon_path, banner_path, game_info)


def favorite_game(game_id, platform):
    GameDBService.add_to_favorites(game_id, platform)


def unfavorite_game(game_id, platform):
    GameDBService.remove_from_favorites(game_id, platform)


def get_favorite_games(platform=None):
    return GameDBService.get_favorite_games(platform)
