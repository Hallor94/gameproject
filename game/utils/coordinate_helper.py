# file: utils/coordinate_helper.py

from utils import globals as G

class CoordinateHelper:

    @staticmethod
    def grid_to_world(grid_x, grid_y):
        tw = G.gamemap.tile_width
        th = G.gamemap.tile_height
        return grid_x * tw, grid_y * th

    @staticmethod
    def world_to_screen(world_x, world_y):
        scale = G.camera_scale
        return (
            int(world_x * scale + G.gamemap.camera.offset_x),
            int(world_y * scale + G.gamemap.camera.offset_y)
        )

    @staticmethod
    def screen_to_world(screen_x, screen_y):
        scale = G.camera_scale
        return (
            int((screen_x - G.gamemap.camera.offset_x) / scale),
            int((screen_y - G.gamemap.camera.offset_y) / scale)
        )

    @staticmethod
    def grid_to_screen(grid_x, grid_y):
        wx, wy = CoordinateHelper.grid_to_world(grid_x, grid_y)
        return CoordinateHelper.world_to_screen(wx, wy)
