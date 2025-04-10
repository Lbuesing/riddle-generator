from Tile import Tile

# 1 = yellow = cross
# 2 = green = square
# 3 = blue = rhombus


class TileGenerator:
    def __init__(self, n, m):
        self.riddle_size_x = n
        self.riddle_size_y = m

    def print_tiles(self):
        for tile in self.tiles:
            print(tile)

    def generate_tiles_from_matrix_list(self, tile_matrix_list):
        tiles = []
        for matrix in tile_matrix_list:
            tiles.append(Tile(matrix, self.riddle_size_x, self.riddle_size_y))
        return tiles
