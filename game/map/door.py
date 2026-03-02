class Door:
    def __init__(self, tile_a, tile_b, direction, open=True):
        """
        Represents a door connecting two adjacent tiles.
        
        Args:
            tile_a (Tile): One of the connected tiles.
            tile_b (Tile): The other connected tile.
            direction (str): "horizontal" or "vertical" — based on layout, not movement.
            open (bool): Whether the door is currently open.
        """
        self.tile_a = tile_a
        self.tile_b = tile_b
        self.direction = direction  # "horizontal" or "vertical"
        self.open = open
