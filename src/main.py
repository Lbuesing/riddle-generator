import json
import os
from typing import List
from RiddleGenerator import RiddleGenerator
from RiddleSolver import RiddleSolver
from SvgGenerator import SvgGenerator
from Tile import Tile
from TileGenerator import TileGenerator
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    CONFIG_FILE=os.getenv("CONFIG_FILE")
    INPUT_PATH=os.getenv("INPUT_PATH")
    OUTPUT_PATH=os.getenv("OUTPUT_PATH")
    OUTPUT_SVG_SUBFOLDER=os.getenv("OUTPUT_SVG_SUBFOLDER")
    with open(os.path.join(INPUT_PATH,CONFIG_FILE)) as config_file:
        config = json.load(config_file)
    RIDDLE_NAME = config["riddle_name"]
    X_DIMENSION = config["dimensions"]["x"]
    Y_DIMENSION = config["dimensions"]["y"]
    TILE_ARRAYS = config["tiles"]
    tileGenerator = TileGenerator(X_DIMENSION,Y_DIMENSION)
    tiles:List[Tile] = tileGenerator.generate_tiles_from_matrix_list(TILE_ARRAYS)

    output_folder_riddles_svg = os.path.join(OUTPUT_PATH,OUTPUT_SVG_SUBFOLDER)
    os.makedirs(output_folder_riddles_svg, exist_ok=True)
    db_name = os.path.join(OUTPUT_PATH,f"{RIDDLE_NAME}.db")
    riddleGenerator = RiddleGenerator(X_DIMENSION,Y_DIMENSION,tiles,db_name)
    decent_riddles=riddleGenerator.decent_riddles
    if len(decent_riddles)==0:
        print("No decent riddles found!")
        exit(0)
    svgGenerator = SvgGenerator(output_folder_riddles_svg,output_folder_riddles_svg)

    for decent_riddle in decent_riddles:
        print(f'Generating svg for {RIDDLE_NAME}_{decent_riddle["id"]}_{decent_riddle["difficulty"]}')
        riddleSolver = RiddleSolver(decent_riddle["riddle"],tiles)
        solution = riddleSolver.solve_riddle()
        svgGenerator.generate_and_save_riddle_svg(decent_riddle["riddle"],f'{RIDDLE_NAME}_{decent_riddle["id"]}_{decent_riddle["difficulty"]}')
        print(f'Generating svg for tiles for riddle {RIDDLE_NAME}_{decent_riddle["id"]}_{decent_riddle["difficulty"]}')
        svgGenerator.generate_and_save_tile_svg(solution,f'{RIDDLE_NAME}_{decent_riddle["id"]}_{decent_riddle["difficulty"]}_tiles')

