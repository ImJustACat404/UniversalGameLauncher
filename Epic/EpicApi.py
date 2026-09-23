import subprocess
import json
import requests


def get_owned_game_list():
    result = subprocess.run(['legendary', 'list', "--json"], stdout=subprocess.PIPE, timeout=30)
    game_list = json.loads(result.stdout)
    return game_list


def get_installed_game_list():
    result = subprocess.run(['legendary', 'list-installed', "--json"], stdout=subprocess.PIPE)
    game_list = json.loads(result.stdout)
    return game_list


def install_game(game_id):
    subprocess.run(['legendary', 'install', game_id], stdout=subprocess.PIPE)


def launch_game(game_id):
    subprocess.run(['legendary', 'launch', game_id], stdout=subprocess.PIPE)


def get_epic_banner(banner_url):
    try:
        banner = requests.get(banner_url, timeout=15).content
    except requests.exceptions.MissingSchema:
        banner = b''
    return banner
