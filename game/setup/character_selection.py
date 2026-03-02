import os
import json

CHARACTER_DIRS = ["data/characters/base", "data/characters/custom"]

# Add factions to each character when loading from JSON:
def load_characters():
    characters = []
    for folder in CHARACTER_DIRS:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                with open(os.path.join(folder, filename), "r") as f:
                    data = json.load(f)
                    data["factions"] = data.get("factions", ["crew"])
                    if "base_name" not in data:
                        raise ValueError(f"{filename} is missing required 'base_name' field.")
                    characters.append(data)
    return characters


