import os

ASSET_DIR = "assets/characters"

class Character:
    def __init__(self, name, base_name, factions=None):
        self.name = name
        self.base_name = base_name  # e.g., "sarge"
        self.factions = factions if factions else ["crew"]
        self.state = "default"  # or "injured", "dead", etc.

    def get_portrait(self):
        path = os.path.join(ASSET_DIR, "portrait", f"{self.base_name}_{self.state}.png")
        if not os.path.exists(path):
            # fallback to default
            path = os.path.join(ASSET_DIR, "portrait", f"{self.base_name}_default.png")
        return path

    def get_standee(self):
        path = os.path.join(ASSET_DIR, "standee", f"{self.base_name}_{self.state}.png")
        if not os.path.exists(path):
            # fallback to default
            path = os.path.join(ASSET_DIR, "standee", f"{self.base_name}_default.png")
        return path
