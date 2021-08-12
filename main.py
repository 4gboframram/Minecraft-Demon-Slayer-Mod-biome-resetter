import json
import os
import time
from glob import glob
from pathlib import Path

import keyboard


def check_biome(minecraft_path, world_name, player_uuid) -> bool:
    """Returns True if the biome is a good biome (mugen train), based on advancement data, else False"""

    world_folder = Path(minecraft_path, "saves", world_name)

    with open(str(Path(world_folder, "advancements", player_uuid + ".json"))) as advancement_file:
        advancement_data = json.load(advancement_file)
        advancement_data = set(advancement_data)
        if 'minecraft:adventure/adventuring_time' in advancement_data:
            # Check if Vanilla biome
            return False
        elif 'kimetsunoyaiba:mission_no_1' in advancement_data or 'kimetsunoyaiba:mission_no_4' in advancement_data:
            # Check if the spawn biome is either of the 2 kimetsu mountains
            return False
        else:
            return True


def create_world(base_world_name, index, wait_time=10.0) -> None:
    """Creates a world using a macro.
    Specifically only for the demon slayer mod by itself, and assumes you want English mode"""
    print("Creating World...")
    time.sleep(wait_time)
    instructions1 = ["tab", "enter", "tab", "tab", "tab", "enter", "ctrl+a", "backspace"]
    instructions2 = ["tab"] * 5 + ["enter"] + ["tab"] * 36 + \
                    ["enter"] + ["tab"] * 4 + ["enter"] + ["tab"] * 7 + ["enter"] + ["tab", "enter"]
    for i in instructions1:
        keyboard.send(i)
        time.sleep(0.1)
    keyboard.write(f'{base_world_name}{index}', delay=0.02)
    for i in instructions2:
        keyboard.send(i)
        time.sleep(0.05)


def world_is_loaded(config, index: int) -> bool:
    """Returns True if the world is loaded"""
    return Path(config['minecraft_path'], "saves", config['world_name'] + str(index), "advancements").exists()


def reset() -> None:
    keyboard.send("esc, " + "tab, " * 8 + "enter")


def start_macro(config):
    time.sleep(2)
    index = config['starting_world_number']
    config = create_config()
    while True:
        world_name = config['world_name'] + str(index)
        create_world(config['world_name'], index, wait_time=3)

        while not world_is_loaded(config, index):
            time.sleep(2)
            print(Path(config['world_name'] + str(index), "advancements"),
                  "does not exist. Checking again in a second")
        print("World is loaded. Checking biome!")
        time.sleep(1)
        if check_biome(config["minecraft_path"], world_name, config['player_uuid']):
            print("Mugen Train found! Exiting...")
            return
        else:
            reset()
            print("Not a Mugen Train. Continuing...")
        index += 1


def create_config():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    if "%APPDATA%" in config['minecraft_path']:
        minecraft_path = config['minecraft_path'].replace("%APPDATA%", os.getenv("APPDATA"))

    else:
        minecraft_path = config['minecraft_path']
    if config['player_uuid'] == "auto":  # doing auto config shit
        saves_folder = Path(minecraft_path, "saves")
        first_world = Path(saves_folder, os.listdir(saves_folder)[0])
        uuid = os.listdir(Path(first_world, "advancements"))[0].strip(".json")
    else:
        uuid = config["player_uuid"]
    if config['starting_world_number'] == "auto":
        saves_folder = Path(minecraft_path, "saves")
        world_path = str(Path(saves_folder, config['world_name']))
        worlds = glob(world_path + '*')
        if not worlds:
            worlds.append('0')

        def find_index(x):
            try:
                x = int(x.replace(world_path, ''))
                return x
            except ValueError:
                return 0

        indices = sorted(list(map(find_index, worlds)))
        config['starting_world_number'] = indices[-1] + 1

    config["player_uuid"] = uuid
    config['minecraft_path'] = minecraft_path
    return config


def main():
    config = create_config()
    print("Press", config['start_shortcut'], "to start")
    keyboard.wait(config['start_shortcut'])
    print("Macro will start in a few seconds. Go to the title screen or else things might happen")

    start_macro(config)


if __name__ == '__main__':
    main()
