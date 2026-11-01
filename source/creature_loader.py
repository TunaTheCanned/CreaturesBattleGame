import json
import pygame
from source.creature import Creature

def load_creature(path):

    try:
        with open(path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        print(f"{path}: not found")
        pygame.quit()
        raise SystemExit
    except json.decoder.JSONDecodeError:
        print(f"{path}: invalid json")
        pygame.quit()
        raise SystemExit


    if not isinstance(data, list):
        raise ValueError("creatures.json must be a list")


    creatures = []
    required = {"name", "hp", "attack", "defense", "evasion", "moves", "sprite"}


    for index, item in enumerate(data, start=1):
        try:
            if not isinstance(item, dict):
                raise ValueError("entry must be an object")

            missing = required - item.keys()
            if missing:
                raise ValueError("missing fields: " + ", ".join(sorted(missing)))

            if not isinstance(item["name"], str):
                raise ValueError("name must be a string")
            for field in ("hp", "attack", "defense", "evasion"):
                if not isinstance(item[field], int) or isinstance(item[field], bool):
                    raise ValueError(f"{field} must be an integer")

            if item["hp"] <= 0 or item["defense"] <= 0 or item["attack"] <= 0:
                raise ValueError("hp, defense and attack must be positive values")
            if not 0 <= item["evasion"] <= 100:
                raise ValueError("evasion must be a positive value between 0 and 100")

            if not isinstance(item["moves"], list) or not all(isinstance(move, str) for move in item["moves"]):
                raise ValueError("moves must be a list of strings")
            if not isinstance(item["sprite"], str):
                raise ValueError("sprite must be a string")

            sprite = pygame.image.load(item['sprite']).convert_alpha()
            creatures.append(Creature(item['name'], item['hp'], item['attack'], item['defense'], item['evasion'], item['moves'], sprite))

        except (ValueError, pygame.error, FileNotFoundError) as error:
            print(f"Creature entry {index} skipped: {error}")


    return creatures


