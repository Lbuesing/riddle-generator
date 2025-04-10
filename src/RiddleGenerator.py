import os
import sqlite3
from typing import List
import numpy as np
from Tile import Tile
import copy


class RiddleGenerator:
    def __init__(self,n,m,tiles,db_name):
        self.riddle_size_x=n
        self.riddle_size_y=m
        self.tiles:list[Tile] = tiles
        self.riddles = {}
        self.riddle_counter = 0
        self.decent_riddles = []
        # Connect to SQLite database
        self.db_path = db_name
        print(f"Connecting to db: {self.db_path}")
        if not os.path.exists(self.db_path):
            self.conn = sqlite3.connect(':memory:')  
            cursor = self.conn.cursor()
            # Create table to store arrays and their counts
            cursor.execute('''
                CREATE TABLE arrays (
                    id INTEGER PRIMARY KEY,
                    array TEXT UNIQUE,
                    count INTEGER,
                    difficulty INTEGER
                                )
            ''')
            self.conn.commit()
            cursor.execute('CREATE INDEX idx_array ON arrays(array)')
            self.conn.commit()
            self.generate_riddles()
            # Retrieve arrays that occur only once
            self.calculate_decent_riddles()
        
            disk_conn = sqlite3.connect(self.db_path)
            self.conn.backup(disk_conn)
            disk_conn.close()
        else:
            self.get_decent_riddles_from_db()
        self.conn.close()

    def calculate_decent_riddles(self):
        """Iterates over all riddles with only one solution, removes duplicates, checks the difficulty
        """

        # Get riddles with only one solution
        cursor = self.conn.cursor()
        cursor.execute('''
                SELECT array 
                FROM arrays 
                WHERE count = 1
            ''')

        decent_riddle_counter = 0

        # Iterate over all found riddles
        for row in cursor:
            cursor2 = self.conn.cursor()
            unique_riddle = np.array(eval(row[0].replace('\n', '')))
            difficulty_classified = self.is_riddle_difficulty_already_classified(cursor2, unique_riddle)
            if not difficulty_classified:
                difficulty = self.calc_difficulty(unique_riddle)
                array_str = self.array_to_string(unique_riddle)
                # Update the difficulty in the db
                cursor2.execute('''
                        UPDATE arrays
                        SET difficulty = ?
                        WHERE array = ?
                    ''', (int(difficulty),array_str,))
                self.conn.commit()
            else:
                difficulty = 0
            if difficulty>0:
                

                print(f"Found unique riddle nr.{decent_riddle_counter+1} with difficulty {difficulty}:")
                print(unique_riddle)
                
                self.decent_riddles.append({"riddle":unique_riddle,
                                                                "difficulty":difficulty,
                                                                "id":decent_riddle_counter})
                decent_riddle_counter +=1

    def is_riddle_difficulty_already_classified(self, cursor2:sqlite3.Cursor, unique_riddle):
        """flips and rotates the given riddle, then checks the db, if any variation is already classified as difficult.

        Args:
            cursor2 (Cursor): cursor of the db
            unique_riddle (ndarray): Numpy array containing the riddle matrix

        Returns:
            boolean:    True, if a riddle is classified as difficult in any of the variations. 
                        False, else
        """

        riddle_flipped_rotated_list=[unique_riddle]
        riddle_rotated = copy.deepcopy(unique_riddle)
        riddle_rotated_flipped = copy.deepcopy(np.flip(unique_riddle,0))
        riddle_flipped_rotated_list.append(riddle_rotated_flipped)
        for i in range(3):
            riddle_rotated = np.rot90(riddle_rotated)
            riddle_rotated_flipped = np.rot90(riddle_rotated_flipped)
            riddle_flipped_rotated_list.append(riddle_rotated)
            riddle_flipped_rotated_list.append(riddle_rotated_flipped)
        found_match = False
        for riddle in riddle_flipped_rotated_list:
            array_str = self.array_to_string(riddle)
            cursor2.execute('''
                    SELECT COUNT(array) 
                    FROM arrays
                    WHERE difficulty > -1 AND array = ?
                ''', (array_str,))
            result = cursor2.fetchone()[0]
            found_match = result>0
            if found_match:
                break
        return found_match

    def get_decent_riddles_from_db(self):
        """ If the difficulty evaluation has been done already, this can be used to get all decent riddles from a db file directly
        """
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
           
        cursor.execute('''
                SELECT array,difficulty
                FROM arrays 
                WHERE count = 1 AND difficulty > 0
            ''')

        unique_arrays = cursor.fetchall()
        decent_riddles = [np.array(eval(array[0].replace('\n', ''))) for array in unique_arrays]
        difficulties = [array[1] for array in unique_arrays]
        for i,decent_riddle in enumerate(decent_riddles):
            self.decent_riddles.append({"riddle":decent_riddle,
                                                    "difficulty":difficulties[i],
                                                    "id":i})


    def generate_riddles(self):
        """ Entrypoint for the recursive process of generating all possible solutions for the given tiles
        """
        solution = np.zeros((self.riddle_size_x,self.riddle_size_y),dtype=int)
        self.recursive_riddler(solution,0, [],False)
        self.recursive_riddler(solution,0, [],True)

    def recursive_riddler(self,solution,tile_id,tile_position_dict_list:list,check_multiple_solutions=False):
        """ Recursively checks all posible solutions on how all tiles could be placed on the given riddle dimensions.

        Args:
            solution (matrix): current state of the riddle solution. Here is stored, where tiles are placed already
            tile_id (int): Id of the current tile in the self.tiles list
            tile_position_dict_list (list): list of all tile position dicts used for the current given solution. These are needed, so the next tile can be evaluated regarding tiles crossing in impossible ways.
        """
        tile:Tile = self.tiles[tile_id]
        if tile_id == 0 and check_multiple_solutions == False:
            tile_positions_dict = tile.possible_positions_no_flip_and_rotation_dict
        elif tile_id == 0 and check_multiple_solutions == True:
            tile_positions_dict = tile.possible_positions_only_flip_and_rotation_dict
        else:
            tile_positions_dict = tile.possible_positions_dict
        for i in tile_positions_dict:
            tile_position_obj = tile_positions_dict[i]
            try:
                new_solution = self.add_tile_to_solution(solution,tile_position_obj,tile_position_dict_list)
               
                if (tile_id == len(self.tiles)-1):  # If last tile was placed:
                    self.add_solution_to_db(new_solution,check_multiple_solutions)
                    self.conn.commit()
                    if (self.riddle_counter%10000==0):
                        print(f"Found solution number {self.riddle_counter} (Check for multiple solutions = {check_multiple_solutions}):")
                        print(new_solution)
                else:
                    tile_position_dict_list.append(tile_position_obj)
                    self.recursive_riddler(new_solution,tile_id+1,tile_position_dict_list,check_multiple_solutions)
                    tile_position_dict_list.pop()
            except MyException as e: # This catches an error thrown by the self.add_tile_to_solution(...) call, if the tile position does not fit into the solution.
                continue

    def add_solution_to_db(self, new_solution,check_multiple_solutions):
        """ Add a solution to db if not existing already, count up, if existing already.

        Args:
            new_solution (List[List]): (new) riddle
        """

        array_str = self.array_to_string(new_solution)
        cursor = self.conn.cursor()
        self.riddle_counter+=1 # This is to track, how many solutions have been calculated already. It does not reflect, how many unique riddles have been calculated yet.
        if check_multiple_solutions:
            cursor.execute('''
                            INSERT INTO arrays (array, count, difficulty)
                            VALUES (?, 1, -1)
                            ON CONFLICT(array) DO UPDATE SET count = count + 1
                        ''', (array_str,))
            
        else:
            cursor.execute('''
                        UPDATE arrays
                        SET count = count + 1
                        WHERE array = ?
                    ''', (array_str,))

    def add_tile_to_solution(self,solution,tile_position_dict,tile_position_dict_list):
        """ Adds a tile to the given solution matrix.

        Args:
            solution (List[List]): current state of the solution
            tile_position_dict (dict): dictionary containing the current tile position
            tile_position_dict_list (List[dict]): List of dictionary with all tile positions added to the solution so far

        Raises:
            MyException: thrown, if the given tile position does not fit

        Returns:
            new_solution: updated solution containing the given tile position
        """

        assert len(solution)==len(tile_position_dict["position"])
        assert len(solution[0])==len(tile_position_dict["position"][0])
        new_solution = copy.deepcopy(solution)
        for x in range(len(solution)):
            for y in range(len(solution[0])):
                #Check if a tile coordinate is already taken in the solution, or if the tile crosses with other tiles:
                if (new_solution[x][y] != 0 and tile_position_dict["position"][x][y] != 0) or (self.do_tiles_cross(tile_position_dict,tile_position_dict_list)):
                    raise MyException("tile_position does not fit!")
                new_solution[x][y] += tile_position_dict["position"][x][y]
        return new_solution
    

    def remove_tile_from_solution(self,solution,tile_position_dict,tile_position_dict_list):
        """ Removes a tile to the given solution matrix.

        Args:
            solution (List[List]): current state of the solution
            tile_position_dict (dict): dictionary containing the current tile position
            tile_position_dict_list (List[dict]): List of dictionary with all tile positions removed from the solution so far

        Raises:
            MyException: thrown, if the given tile position does not fit

        Returns:
            new_solution: updated solution without the given tile position
        """
        
        assert len(solution)==len(tile_position_dict["position"])
        assert len(solution[0])==len(tile_position_dict["position"][0])
        new_solution = copy.deepcopy(solution)
        for x in range(len(solution)):
            for y in range(len(solution[0])):
                
                if (tile_position_dict["position"][x][y] != 0 and new_solution[x][y] - tile_position_dict["position"][x][y] != 0) or(self.do_tiles_cross(tile_position_dict,tile_position_dict_list)):
                    raise MyException("tile_position does not fit!")
                new_solution[x][y] -= tile_position_dict["position"][x][y]
        return new_solution
    
    def do_tiles_cross(self,tile_position:dict,tile_positions:List[dict]):
        """ Checks if the given tiles crosses any of the tiles in the tile_position_dict_list.

        Args:
            tile_position_dict (dict): dictionary containing the current tile position
            tile_position_dict_list (List[dict]): List of dictionary with multiple tile positions

        Returns:
            boolean: True, if tile crosses any other position. False, else.
        """

        for tile_position_list in tile_positions:
            for diagonal_coordinates_outer in tile_position["diagonal_coordinates"]:
                for diagonal_coordinates_inner in tile_position_list["diagonal_coordinates"]:
                    if self.is_intersect(diagonal_coordinates_outer,diagonal_coordinates_inner):
                        return True
        return False

    def calc_difficulty(self,riddle):
        """ Calculates the difficulty of a riddle

        Args:
            riddle (List[List]): input riddle

        Returns:
            difficulty
        """
        
        riddle_heatmap,tile_fits = self.generate_riddle_heatmap(riddle)

        difficulty = 1
        max_difficulty = 1000
        for tile_fit in tile_fits:
            number_fits = tile_fits[tile_fit]["number_fits"]
            max_difficulty = min(max(number_fits-1,0),max_difficulty) # maximum difficulty should be limited to the worst number_fit values found
            difficulty = difficulty*(max(number_fits-1,0))
            if difficulty > 0:
                difficulty=max_difficulty
        difficulty1=difficulty
        
        if difficulty != 0:
            difficulty = 1
            max_difficulty = 1000
            for x in range(len(riddle_heatmap)):
                for y in range(len(riddle_heatmap[0])):
                    if riddle_heatmap[x][y]>0:
                        difficulty = difficulty*(max(riddle_heatmap[x][y]-1,0))
                        max_difficulty = min(max(riddle_heatmap[x][y]-1,0),max_difficulty) # maximum difficulty should be limited to the worst values found in the heatmap
                        if difficulty > 0:
                            difficulty=max_difficulty
        else:
            return 0
        difficulty2=difficulty   
        if difficulty != 0:
            difficulty = 1
            max_difficulty = 1000
            for tile_fit in tile_fits:
                reacheability = tile_fits[tile_fit]["reacheability"]
                max_difficulty = min(max(reacheability-1,0),max_difficulty) # maximum difficulty should be limited to the worst reacheability values found
                difficulty = difficulty*(max(reacheability-1,0))
                if difficulty > 0:
                    difficulty=max_difficulty
        else:
            return 0
        difficulty = min(difficulty,9)+(100 * min(difficulty1,9))+(10 * min(difficulty2,9))

        return difficulty

    def generate_riddle_heatmap(self, riddle):
        """ Generates data, on which the difficulty can be evaluated such as:
            -how many positions can a tile fit inside a riddle
            -if a tile is placed inside the riddle, are all coordinates reacheable by any other tile?
            -how many tile positions cover each riddle position

        Args:
            riddle (List[List]): input riddle

        Returns:
            riddle_heatmap,tile_fits
        """
        tile_fits = {}
        riddle_heatmap = np.zeros((self.riddle_size_x,self.riddle_size_y),dtype=int) # This will contain information, how many tile positions cover each riddle coordinate.
        for i,tile in enumerate(self.tiles):
            tile_fits[i]={}
            tile_fits[i]["number_fits"]=0 # Count, how many positions of a tile would fit into the riddle.
            tile_fits[i]["reacheability"]=0 # If a tile position fit, and all other riddle coordinates can be reached by any other tile still, count up.
        
            for position_dict_key in tile.possible_positions_dict:
                position_dict = tile.possible_positions_dict[position_dict_key]
                if self.tile_fits(position_dict["position"],riddle):
                    tile_fits[i]["number_fits"]+=1
                    tiles = copy.deepcopy(self.tiles)
                    tiles.pop(i)
                    if self.are_all_riddle_coordinates_reacheable(riddle,position_dict,tiles):
                        tile_fits[i]["reacheability"]+=1
                    for x in range(len(riddle_heatmap)):
                        for y in range(len(riddle_heatmap[0])):
                            if position_dict["position"][x][y] > 0:
                                riddle_heatmap[x][y] += 1
        return riddle_heatmap, tile_fits 

    def are_all_riddle_coordinates_reacheable(self, riddle,tile_position:dict,tiles:List[Tile]):
        """ Checks if a tile position fits, and all other riddle coordinates can be reached by any other tile still.

        Args:
            riddle (List[List]): input riddle
            tile_position (dict): tile position info
            tiles (List[Tile]): list of all tiles except the one belonging to the given tile_position

        Returns:
            boolean: True, if all other riddle positions are still reacheable by any tile after placing the given one
        """
        riddle_state = self.remove_tile_from_solution(riddle,tile_position,[])
        for tile in tiles:
            tile_fits = False
            for position_dict_key in tile.possible_positions_dict:
                position_dict = tile.possible_positions_dict[position_dict_key]
                try:
                    self.remove_tile_from_solution(riddle_state,position_dict,[tile_position])
                    tile_fits == True
                except MyException as e:
                    continue
            if tile_fits == False:
                return False
        return True
    
    def tile_fits(self,tile_position,riddle):
        """ Checks if the tile fits inside the riddle

        Args:
            tile_position (List[List]): tile position matrix
            riddle (List[List]): input riddle matrix

        Returns:
            boolean: True, if tile fits inside the riddle
        """

        for x in range(len(riddle)):
            for y in range(len(riddle[0])):
                if tile_position[x][y] != 0:
                    if tile_position[x][y] - riddle[x][y] != 0:
                        return False
        return True
    
    def is_intersect(self, positions1:List[tuple], positions2:List[tuple]):
        """ Checks if two lines defined by positions1 and positions2 intersect.

        Args:
            positions1 (List[tuple]): line coordinates 1
            positions2 (List[tuple]): line coordinates 2

        Returns:
            _type_: _description_
        """
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
        return False
    

    def array_to_string(self,array):
        """ Transforms an array into a string. This is needed for the sqlite db to be able to store the array.

        Args:
            array (array): given array

        Returns:
            str: array converted to string
        """
        return np.array2string(array, separator=',')
class MyException(Exception):
    pass