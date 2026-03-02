
class Player:
    def __init__(self, name, character_data):
        self.name = name
        self.character = character_data["name"]
        self.hp = character_data["hp"]
        self.move = character_data["move"]
        self.attack = character_data["attack"]

    def __repr__(self):
        return f"<Player {self.name}: {self.character} (HP: {self.hp}, Move: {self.move}, Atk: {self.attack})>"
