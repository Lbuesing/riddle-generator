import copy
import numpy as np
from typing import List,Tuple
class Tile:
    def __init__(self,tile_matrix,n,m):
        self.tile_matrix = tile_matrix
        self.possible_positions = None
        self.possible_positions_no_flip_and_rotation = []
        self.possible_positions_only_flip_and_rotation = []
        print(self)
        self.set_possible_positions(n,m)
        self.possible_positions_dict = self.generate_position_dict(self.possible_positions)
        self.possible_positions_no_flip_and_rotation_dict = self.generate_position_dict(self.possible_positions_no_flip_and_rotation)
        self.possible_positions_only_flip_and_rotation_dict = self.generate_position_dict(self.possible_positions_only_flip_and_rotation)
        # print(self.possible_positions)

    def set_possible_positions(self,n,m):
        self.possible_positions=[]
        tile_size_x = len(self.tile_matrix)
        tile_size_y = len(self.tile_matrix[0])
        for x_field in range(n-tile_size_x+1):
            for y_field in range(m-tile_size_y+1):
                full_field=np.zeros((n,m),dtype=int)
                for x_tile in range(tile_size_x):
                    for y_tile in range(tile_size_y):
                        full_field[x_field+x_tile,y_field+y_tile]=self.tile_matrix[x_tile][y_tile]
                self.possible_positions.append(full_field)
                self.possible_positions_no_flip_and_rotation.append(full_field)
                self.possible_positions.append(np.flip(full_field,0))
                full_field_rotated = copy.deepcopy(full_field)
                full_field_rotated_flipped = copy.deepcopy(np.flip(full_field,0))
                for i in range(3):
                    full_field_rotated = np.rot90(full_field_rotated)
                    full_field_rotated_flipped = np.rot90(full_field_rotated_flipped)
                    self.possible_positions.append(full_field_rotated)
                    self.possible_positions.append(full_field_rotated_flipped)
        # self.possible_positions= [np.unique(subarr) for subarr in self.possible_positions]        
        # Use dictionary to remove duplicates
        number_of_solutions=len(self.possible_positions)
        self.possible_positions = [np.array(tup) for tup in {array_to_tuple(arr): arr for arr in self.possible_positions}]
        self.possible_positions_only_flip_and_rotation = [entry for entry in self.possible_positions if array_to_tuple(entry) not in set([array_to_tuple(entry2) for entry2 in self.possible_positions_no_flip_and_rotation])]
        print(f"Removed {number_of_solutions-len(self.possible_positions)} duplicate positions. Found {len(self.possible_positions)} unique possible positions! \n\
              Found {len(self.possible_positions_no_flip_and_rotation)} positions without flips and rotation.\n\
                Found {len(self.possible_positions_only_flip_and_rotation)} positions with only flips and rotation.")
    
    def generate_position_dict(self,matrix_list):
        positions_dict = {}
        for i,matrix in enumerate(matrix_list):
            coordinates=self.find_coordinates(matrix)
            diagonal_coordinates=self.find_diagonal_coordinates(coordinates)
            positions_dict[i]={"position":matrix,
                              "diagonal_coordinates":diagonal_coordinates}
        return positions_dict

    def find_diagonal_coordinates(self,coordinates:List[Tuple[int,int]]):
        diagonal_coordinates =[]
        for coordinate in coordinates:
            if (coordinate[0]+1,coordinate[1]+1) in coordinates:
                if (coordinate[0],coordinate[1]+1) not in coordinates and (coordinate[0]+1,coordinate[1]) not in coordinates: 
                    diagonal_coordinates.append([coordinate,(coordinate[0]+1,coordinate[1]+1)])
            if (coordinate[0]-1,coordinate[1]+1) in coordinates:
                if (coordinate[0],coordinate[1]+1) not in coordinates and (coordinate[0]-1,coordinate[1]) not in coordinates: 
                    diagonal_coordinates.append([coordinate,(coordinate[0]-1,coordinate[1]+1)])


        return diagonal_coordinates
    
    def find_coordinates(self,matrix):
        coordinates = []
        for x_matrix in range(len(matrix)):
            for y_matrix in range(len(matrix[0])):
                if matrix[x_matrix][y_matrix] > 0:
                    coordinate = (x_matrix,y_matrix)
                    coordinates.append((x_matrix,y_matrix))
        return coordinates



    def __str__(self):
        string = ""
        for list in self.tile_matrix:
            string = string + str(list) + "\n"
        return string
def array_to_tuple(array):
    return tuple(map(tuple, array))
