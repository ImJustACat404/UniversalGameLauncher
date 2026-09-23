from abc import ABC, abstractmethod
import os
import Epic.EpicApi as EpicApi
import pygame
pygame.init()


# Constants
ICON_SIZE = 28, 28
BANNER_SIZE = 240, 360
MISSING_BANNER = "Img/NoBanner.jpg"
MISSING_ICON = "Img/NoIcon.jpg"


class Game(ABC):
    def __init__(self, name, icon_path, banner_path, notes, info):
        self.name = name
        try:
            unscaled_icon = pygame.image.load(icon_path)
        except pygame.error:
            unscaled_icon = pygame.image.load(MISSING_ICON)
        self.icon = pygame.transform.smoothscale(unscaled_icon.convert_alpha(), ICON_SIZE)
        try:
            unscaled_banner = pygame.image.load(banner_path)
        except pygame.error:
            unscaled_banner = pygame.image.load(MISSING_BANNER)
        unscaled_size = unscaled_banner.get_width(), unscaled_banner.get_height()
        self.banner = pygame.transform.smoothscale(unscaled_banner.convert_alpha(), (BANNER_SIZE[0], (BANNER_SIZE[0] * unscaled_size[1]) // unscaled_size[0]))
        self.notes = notes
        self.info = info

    def get_name(self):
        return self.name

    def get_notes(self):
        return self.notes

    def set_notes(self, notes):
        self.notes = notes

    def get_banner(self):
        return self.banner

    def get_icon(self):
        return self.icon

    def get_info(self):
        return self.info

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def get_platform(self):
        return 'Game'


class ExeGame(Game):
    def __init__(self, name, icon_path, banner_path, notes, exe_path, game_id, info):
        super().__init__(name, icon_path, banner_path, notes, info)
        self.exe_path = exe_path
        self.game_id = game_id

    def start(self):
        os.chdir('/'.join((self.exe_path.split('/')[:-1])))
        print(self.exe_path.split('/')[-1])
        os.system('\"' + self.exe_path.split('/')[-1] + '\"')

    def get_platform(self):
        return 'Other'

    def get_id(self):
        return self.game_id


class SteamGame(Game):
    def __init__(self, name, icon_path, banner_path, notes, game_id, info, playtime):
        super().__init__(name, icon_path, banner_path, notes, info)
        self.game_id = game_id
        self.playtime = playtime

    def get_platform(self):
        return "Steam"

    def get_id(self):
        return self.game_id

    def start(self):
        os.system(f"start \"\" steam://rungameid/{self.game_id}")


class EpicGame(Game):
    def __init__(self, name, icon_path, banner_path, notes, game_id, info):
        super().__init__(name, icon_path, banner_path, notes, info)
        self.game_id = game_id

    def get_platform(self):
        return "Epic"

    def get_id(self):
        return self.game_id

    def start(self):
        EpicApi.launch_game(self.game_id)
