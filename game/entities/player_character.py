# file: entities/player_character.py

class PlayerCharacter:
    def __init__(self, char_id, display_name, full_name, description, base_type, scale,
                 strength, endurance, dexterity, intelligence, nerve, luck,
                 health_base, move_points_base, attack_base):
        self.char_id = char_id
        self.display_name = display_name
        self.full_name = full_name
        self.description = description
        self.base_type = base_type
        self.scale = scale

        # Core stats
        self.strength = strength
        self.endurance = endurance
        self.dexterity = dexterity
        self.intelligence = intelligence
        self.nerve = nerve
        self.luck = luck

        # Derived stats
        self.health_base = health_base
        self.move_points_base = move_points_base
        self.attack_base = attack_base

    @classmethod
    def create_random_placeholder(cls):
        return cls(
            char_id="unknown",
            display_name="Random",
            full_name="Random Character",
            description="If selected, a random unused character will be assigned.",
            base_type="unknown",
            scale=1.0,
            strength=0,
            endurance=0,
            dexterity=0,
            intelligence=0,
            nerve=0,
            luck=0,
            health_base=0,
            move_points_base=0,
            attack_base=0
        )