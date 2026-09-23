__author__ = "Ido Senn"

import sqlite3
import sys
import threading


RUN_LOCATION = '\\'.join(sys.argv[0].split('\\')[:-1])
DATABASE_LOCATION = RUN_LOCATION + "\\Data\\Games.db"
DB_LOCK = threading.Lock()


def add_exe_game(name, exe_path, icon_path, banner_path, game_info):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "INSERT INTO ExeGame (Name, ExePath, IconPath, BannerPath, Notes, GameInfo) VALUES (?, ?, ?, ?, ?, ?)"
        db_cursor.execute(query, (name, exe_path, icon_path, banner_path, "", game_info))
        game_id = db_cursor.lastrowid
        database.commit()
        db_cursor.close()
        database.close()
    return game_id


def get_exe_games():
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT Name, ExePath, IconPath, BannerPath, Notes, ID, GameInfo from ExeGame ORDER BY Name'
        db_cursor.execute(query)
        game_data = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return game_data


def remove_exe_game(game_id):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "DELETE FROM ExeGame WHERE ID = ?"
        db_cursor.execute(query, (game_id,))
        database.commit()
        db_cursor.close()
        database.close()


def add_steam_game(game_id, name, playtime, icon_path, banner_path, game_info):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "INSERT INTO SteamGames (ID, Name, Playtime, IconPath, BannerPath, Notes, GameInfo) VALUES (?, ?, ?, ?, ?, ?, ?)"
        db_cursor.execute(query, (game_id, name, playtime, icon_path, banner_path, "", game_info))
        game_id = db_cursor.lastrowid
        database.commit()
        db_cursor.close()
        database.close()
    return game_id


def get_steam_games():
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT ID, Name, Playtime, IconPath, BannerPath, Notes, GameInfo from SteamGames ORDER BY Name'
        db_cursor.execute(query)
        game_data = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return game_data


def get_steam_game_id_list():
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT ID from SteamGames'
        db_cursor.execute(query)
        id_tuples = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return [id_tuple[0] for id_tuple in id_tuples]


def remove_steam_game(game_id):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "DELETE FROM SteamGames WHERE ID = ?"
        db_cursor.execute(query, (game_id,))
        database.commit()
        db_cursor.close()
        database.close()


def update_steam_notes(game_id, notes):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "UPDATE SteamGames SET Notes = ? WHERE ID = ?"
        db_cursor.execute(query, (notes, game_id))
        database.commit()
        db_cursor.close()
        database.close()


def update_exe_notes(game_id, notes):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "UPDATE ExeGame SET Notes = ? WHERE ID = ?"
        db_cursor.execute(query, (notes, game_id))
        database.commit()
        db_cursor.close()
        database.close()


def add_epic_game(game_id, name, icon_path, banner_path, game_info):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "INSERT INTO EpicGames (ID, Name, IconPath, BannerPath, Notes, GameInfo) VALUES ( ?, ?, ?, ?, ?, ?)"
        db_cursor.execute(query, (game_id, name, icon_path, banner_path, "", game_info))
        game_id = db_cursor.lastrowid
        database.commit()
        db_cursor.close()
        database.close()
    return game_id


def get_epic_games():
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT ID, Name, IconPath, BannerPath, Notes, GameInfo from EpicGames ORDER BY Name'
        db_cursor.execute(query)
        game_data = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return game_data


def get_epic_game_id_list():
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = 'SELECT ID from EpicGames'
        db_cursor.execute(query)
        id_tuples = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return [id_tuple[0] for id_tuple in id_tuples]


def remove_epic_game(game_id):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "DELETE FROM EpicGames WHERE ID = ?"
        db_cursor.execute(query, (game_id,))
        database.commit()
        db_cursor.close()
        database.close()


def update_epic_notes(game_id, notes):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "UPDATE EpicGames SET Notes = ? WHERE ID = ?"
        db_cursor.execute(query, (notes, game_id))
        database.commit()
        db_cursor.close()
        database.close()


def add_to_favorites(game_id, platform):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "INSERT INTO Favorites (Platform, ID) VALUES (?, ?)"
        db_cursor.execute(query, (platform, game_id))
        database.commit()
        db_cursor.close()
        database.close()


def remove_from_favorites(game_id, platform):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        query = "DELETE FROM Favorites WHERE ID = ? AND Platform = ?"
        db_cursor.execute(query, (game_id, platform))
        database.commit()
        db_cursor.close()
        database.close()


def get_favorite_games(platform=None):
    with DB_LOCK:
        database = sqlite3.connect(DATABASE_LOCATION)
        db_cursor = database.cursor()
        if platform is None:
            query = 'SELECT Platform, ID from Favorites'
            db_cursor.execute(query)
        else:
            query = 'SELECT Platform, ID from Favorites WHERE Platform = ?'
            db_cursor.execute(query, (platform,))
        favorites = db_cursor.fetchall()
        db_cursor.close()
        database.close()
    return favorites


def main():
    global DATABASE_LOCATION
    DATABASE_LOCATION = "Games.db"
    games = get_favorite_games(platform="Steam")
    print(games)


if __name__ == "__main__":
    main()
