import copy
from typing import List

from Tile import Tile

class RiddleSolver():
    def __init__(self,riddle_matrix,tiles:List[Tile]):
        self.riddle_matrix = riddle_matrix
        self.tiles = tiles


    def solve_riddle(self):
        return self.recursive_solver(self.riddle_matrix,0,[])

    def recursive_solver(self,solution,tile_id,tile_position_dict_list:list):
        tile:Tile = self.tiles[tile_id]
        tile_positions_dict = tile.possible_positions_dict

        for i in tile_positions_dict:
            tile_position_obj = tile_positions_dict[i]
            try:
                new_solution = self.add_tile_to_solution(solution,tile_position_obj,tile_position_dict_list)
                if (tile_id == len(self.tiles)-1):
                    tile_position_dict_list.append(tile_position_obj)
                    return tile_position_dict_list
                else:
                    tile_position_dict_list.append(tile_position_obj)
                    tile_position_dict_list_solution = self.recursive_solver(new_solution,tile_id+1,tile_position_dict_list)
                    if len(tile_position_dict_list_solution) == len(self.tiles):
                        return tile_position_dict_list_solution
                    tile_position_dict_list.pop()
            except MyException as e:
                continue
        return []

    def add_tile_to_solution(self,solution,tile_position_dict,tile_position_dict_list):
        assert len(solution)==len(tile_position_dict["position"])
        assert len(solution[0])==len(tile_position_dict["position"][0])
        new_solution = copy.deepcopy(solution)
        for x in range(len(solution)):
            for y in range(len(solution[0])):
                if (new_solution[x][y] - tile_position_dict["position"][x][y] != 0 and tile_position_dict["position"][x][y]!=0) or (self.do_tiles_cross(tile_position_dict,tile_position_dict_list)):
                    raise MyException("tile_position does not fit!")
                new_solution[x][y] -= tile_position_dict["position"][x][y]
        return new_solution
    
    def do_tiles_cross(self,tile_position_dict,tile_position_dict_list):
        for tile_position_dict_from_list in tile_position_dict_list:
            for diagonal_coordinates_outer in tile_position_dict["diagonal_coordinates"]:
                for diagonal_coordinates_inner in tile_position_dict_from_list["diagonal_coordinates"]:
                    if self.is_intersect(diagonal_coordinates_outer,diagonal_coordinates_inner):
                        return True
        return False    
    def is_intersect(self, positions1, positions2):
        (x1, y1) = positions1[0]
        (x2, y2) = positions1[1]
        (x3, y3) = positions2[0]
        (x4, y4) = positions2[1]
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return False
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
        if 0 < t < 1 and 0 < u < 1:
            return True
class MyException(Exception):
    pass