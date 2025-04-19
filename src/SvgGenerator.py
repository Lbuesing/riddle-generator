import os
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath


class SvgGenerator:
    def __init__(self, output_folder_riddles, output_folder_pieces):
        self.output_folder_riddles = output_folder_riddles
        self.output_folder_pieces = output_folder_pieces

    def generate_and_save_riddle_svg(self, riddle_matrix, riddle_id,tolerance=0):
        combined_cubes = self.combine_cubes_to_riddle(riddle_matrix, cube_size=1.0,tolerance=tolerance)
        # patch_list = self.generate_outline_patches(riddle_matrix,cube_size=1.0)
        self.export_shape(combined_cubes, [], os.path.join(self.output_folder_riddles, f"{riddle_id}_riddle.svg"), False)

    def generate_and_save_tile_svg(self, tile_list, tile_id):
        all_combined_shapes = []
        all_patch_list = []
        for tile in tile_list:
            combined_shapes = self.combine_shapes_to_tile(tile["position"], cube_size=1.0)
            patch_list = self.generate_outline_patches(tile["position"], cube_size=1.0)

            all_combined_shapes.extend(combined_shapes)
            all_patch_list.extend(patch_list)
        self.export_shape(
            all_combined_shapes, all_patch_list, os.path.join(self.output_folder_pieces, f"{tile_id}_tiles.svg"), True, True, os.path.join(self.output_folder_pieces, f"{tile_id}_backplate.svg")
        )

    def generate_outline_patches(self, matrix, cube_size):
        inner_shape_size = cube_size - 0.1
        patch_list = []
        for x in range(len(matrix)):
            for y in range(len(matrix[0])):
                if matrix[x][y] != 0:
                    self.draw_inner_octagons(matrix, cube_size, inner_shape_size, patch_list, x, y)
                    self.draw_outer_octagons(matrix, cube_size, inner_shape_size, patch_list, x, y)
        return patch_list

    def draw_inner_octagons(self, matrix, cube_size, inner_circle_size, patch_list: List, x, y):
        if x == 0 or matrix[x - 1][y] == 0:
            patch_list.extend(self.generate_octagon_patches((x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), inner_circle_size, [3]))
        if y == 0 or matrix[x][y - 1] == 0:
            patch_list.extend(self.generate_octagon_patches((x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), inner_circle_size, [5]))
        if x == len(matrix) - 1 or matrix[x + 1][y] == 0:
            patch_list.extend(self.generate_octagon_patches((x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), inner_circle_size, [7]))
        if y == len(matrix[0]) - 1 or matrix[x][y + 1] == 0:
            patch_list.extend(self.generate_octagon_patches((x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), inner_circle_size, [1]))
        if ((x == 0 or y == 0) or (x > 0 and y > 0 and matrix[x - 1][y - 1] == 0)) and not ((x > 0 and matrix[x - 1][y] != 0) and (y > 0 and matrix[x][y - 1] != 0)):
            patch_list.extend(self.generate_octagon_patches((x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), inner_circle_size, [4]))
        if ((x == 0 or y == len(matrix[0]) - 1) or (x > 0 and y < len(matrix[0]) - 1 and matrix[x - 1][y + 1] == 0)) and not (
            (x > 0 and matrix[x - 1][y] != 0) and (y < len(matrix[0]) - 1 and matrix[x][y + 1] != 0)
        ):
            patch_list.extend(self.generate_octagon_patches((x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), inner_circle_size, [2]))
        if ((x == len(matrix) - 1 or y == len(matrix[0]) - 1) or (x < len(matrix) - 1 and y < len(matrix[0]) - 1 and matrix[x + 1][y + 1] == 0)) and not (
            (x < len(matrix) - 1 and matrix[x + 1][y] != 0) and (y < len(matrix[0]) - 1 and matrix[x][y + 1] != 0)
        ):
            patch_list.extend(self.generate_octagon_patches((x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), inner_circle_size, [0]))
        if ((x == len(matrix) - 1 or y == 0) or (x < len(matrix) - 1 and y > 0 and matrix[x + 1][y - 1] == 0)) and not (
            (x < len(matrix) - 1 and matrix[x + 1][y] != 0) and (y > 0 and matrix[x][y - 1] != 0)
        ):
            patch_list.extend(self.generate_octagon_patches((x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), inner_circle_size, [6]))

    def draw_outer_octagons(self, matrix, cube_size, inner_circle_size, patch_list, x, y):
        if (x < len(matrix) - 1 and matrix[x + 1][y] != 0) and (y == len(matrix[0]) - 1 or (y < len(matrix[0]) - 1 and matrix[x + 1][y + 1] == 0 and matrix[x][y + 1] == 0)):
            patch_list.extend(
                self.generate_octagon_connection_patches(
                    inner_circle_size, (x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), (x * cube_size + cube_size * 1.5, y * cube_size + cube_size / 2), 7, 3, False, True
                )
            )
        if (x < len(matrix) - 1 and matrix[x + 1][y] != 0) and (y == 0 or ((y > 0 and matrix[x + 1][y - 1] == 0) and matrix[x][y - 1] == 0)):
            patch_list.extend(
                self.generate_octagon_connection_patches(
                    inner_circle_size, (x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), (x * cube_size + cube_size * 1.5, y * cube_size + cube_size / 2), 7, 3, True, False
                )
            )
        if (y < len(matrix[0]) - 1 and matrix[x][y + 1] != 0) and (x == len(matrix) - 1 or (x < len(matrix) - 1 and matrix[x + 1][y + 1] == 0 and matrix[x + 1][y] == 0)):
            patch_list.extend(
                self.generate_octagon_connection_patches(
                    inner_circle_size, (x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), (x * cube_size + cube_size / 2, y * cube_size + cube_size * 1.5), 1, 5, True, False
                )
            )
        if (y < len(matrix[0]) - 1 and matrix[x][y + 1] != 0) and (x == 0 or (x > 0 and matrix[x - 1][y + 1] == 0 and matrix[x - 1][y] == 0)):
            patch_list.extend(
                self.generate_octagon_connection_patches(
                    inner_circle_size, (x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), (x * cube_size + cube_size / 2, y * cube_size + cube_size * 1.5), 1, 5, False, True
                )
            )

        if (x < len(matrix) - 1 and matrix[x + 1][y] == 0) and (y < len(matrix[0]) - 1 and matrix[x + 1][y + 1] != 0):
            patch_list.extend(
                self.generate_octagon_connection_patches(
                    inner_circle_size, (x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), (x * cube_size + cube_size * 1.5, y * cube_size + cube_size * 1.5), 7, 5, False, True
                )
            )
        if (x < len(matrix) - 1 and matrix[x + 1][y] == 0) and (y > 0 and matrix[x + 1][y - 1] != 0):
            patch_list.extend(
                self.generate_octagon_connection_patches(
                    inner_circle_size, (x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), (x * cube_size + cube_size * 1.5, (y - 1) * cube_size + cube_size / 2), 7, 1, True, False
                )
            )
        if (x > 0 and matrix[x - 1][y] == 0) and (x > 0 and y > 0 and matrix[x - 1][y - 1] != 0):
            patch_list.extend(
                self.generate_octagon_connection_patches(
                    inner_circle_size, (x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), ((x - 1) * cube_size + cube_size / 2, (y - 1) * cube_size + cube_size / 2), 3, 1, False, True
                )
            )
        if (x > 0 and matrix[x - 1][y] == 0) and (x > 0 and y < len(matrix[0]) - 1 and matrix[x - 1][y + 1] != 0):
            patch_list.extend(
                self.generate_octagon_connection_patches(
                    inner_circle_size, (x * cube_size + cube_size / 2, y * cube_size + cube_size / 2), ((x - 1) * cube_size + cube_size / 2, (y + 1) * cube_size + cube_size / 2), 3, 5, True, False
                )
            )

    def combine_cubes_to_riddle(self, matrix, cube_size=1.0,tolerance=0.05):
        shapes = []
        for x in range(len(matrix)):
            for y in range(len(matrix[0])):
                if matrix[x][y] == 0:
                    shape = self.generate_square(cube_size=cube_size,tolerance=tolerance)
                elif matrix[x][y] == 1:
                    shape = self.generate_square_with_hole(cube_size=cube_size, hole_type="square",tolerance=tolerance)
                elif matrix[x][y] == 2:
                    shape = self.generate_square_with_hole(cube_size=cube_size, hole_type="cross",tolerance=tolerance)
                elif matrix[x][y] == 3:
                    shape = self.generate_square_with_hole(cube_size=cube_size, hole_type="circle",tolerance=tolerance)
                shape["position"] = (cube_size * x, cube_size * y)
                shapes.append(shape)
        return shapes

    def export_shape(self, shapes, patch_list, filename, inner_square=False, back_plate=False, back_plate_name=None):
        output_size = 9.5
        fig, ax = plt.subplots(figsize=(output_size / 2.54, output_size / 2.54))
        ax.set_aspect("equal")
        ax.grid(True)
        ax.set_axis_off()
        # Calculate the dimensions of the large square
        max_x = max(shape["position"][0] + (shape.get("size", 0) or shape.get("width", 0) or shape.get("radius", 0) * 2 or shape.get("cube_size", 0)) for shape in shapes)
        max_y = max(shape["position"][1] + (shape.get("size", 0) or shape.get("height", 0) or shape.get("radius", 0) * 2 or shape.get("cube_size", 0)) for shape in shapes)
        box_offset = 0.05
        outer_box_offset = 0.3
        ax_lim_tolerance = 0.015
        # Add the large square that surrounds the whole matrix
        if inner_square:
            ax.add_patch(patches.Rectangle((0 - box_offset, 0 - box_offset), max_x + (2 * box_offset), max_y + (2 * box_offset), fill=False, edgecolor="black", linewidth=1))

        ax.add_patch(self.generate_smothe_rectangle(-outer_box_offset, -outer_box_offset, max_x + 2 * outer_box_offset, max_y + 2 * outer_box_offset, 0.2))

        for shape in shapes:
            if shape["type"] == "square":
                continue
                ax.add_patch(patches.Rectangle(shape["position"], shape["size"], shape["size"], fill=False))
            elif shape["type"] == "square_with_hole":
                # ax.add_patch(patches.Rectangle(shape['position'], shape['size'], shape['size'], fill=False))
                if shape["hole_type"] == "square":
                    hole_size = shape["size"] * 0.4 - shape["tolerance"]
                    hole_position = (shape["position"][0] + shape["size"] * 0.3+shape["tolerance"]/2, shape["position"][1] + shape["size"] * 0.3+shape["tolerance"]/2)
                    ax.add_patch(patches.Rectangle(hole_position, hole_size, hole_size, fill=False))
                elif shape["hole_type"] == "cross":
                    cross_path = self.generate_cross_path(shape["position"], shape["size"] * 0.6 - shape["tolerance"])
                    ax.add_patch(patches.PathPatch(cross_path, fill=False))
                elif shape["hole_type"] == "circle":
                    hole_radius = shape["size"] * 0.25 - shape["tolerance"]/2
                    hole_center = (shape["position"][0] + shape["size"] / 2 , shape["position"][1] + shape["size"] / 2 )
                    ax.add_patch(patches.Circle(hole_center, hole_radius, fill=False))
            elif shape["type"] == "circle":
                ax.add_patch(patches.Circle(shape["position"], shape["radius"], fill=False))
            elif shape["type"] == "rectangle":
                ax.add_patch(patches.Rectangle(shape["position"], shape["width"], shape["height"], angle=shape.get("angle", 0), fill=False))
            elif shape["type"] == "cross":
                cross_path = self.generate_cross_path(shape["position"], shape["cube_size"])
                ax.add_patch(patches.PathPatch(cross_path, fill=False))

        for patch in patch_list:
            ax.add_patch(patch)
        ax.set_xlim(0 - outer_box_offset - ax_lim_tolerance, max_x + outer_box_offset + ax_lim_tolerance)
        ax.set_ylim(0 - outer_box_offset - ax_lim_tolerance, max_y + outer_box_offset + ax_lim_tolerance)

        plt.savefig(filename, format="svg", bbox_inches="tight", pad_inches=0, dpi=96)
        plt.close()
        if back_plate:
            fig, ax = plt.subplots(figsize=(output_size / 2.54, output_size / 2.54))
            ax.set_aspect("equal")
            ax.grid(True)
            ax.set_axis_off()
            ax.add_patch(self.generate_smothe_rectangle(-outer_box_offset, -outer_box_offset, max_x + 2 * outer_box_offset, max_y + 2 * outer_box_offset, 0.2))
            ax.set_xlim(0 - outer_box_offset - ax_lim_tolerance, max_x + outer_box_offset + ax_lim_tolerance)
            ax.set_ylim(0 - outer_box_offset - ax_lim_tolerance, max_y + outer_box_offset + ax_lim_tolerance)

            plt.savefig(back_plate_name, format="svg", bbox_inches="tight", pad_inches=0, dpi=96)
            plt.close()

    def generate_square(self, cube_size=1.0,tolerance=0.0):
        return {"type": "square", "size": cube_size, "tolerance":tolerance}

    def generate_square_with_hole(self, cube_size=1.0, hole_type="square",tolerance=0.0):
        return {"type": "square_with_hole", "size": cube_size, "hole_type": hole_type, "tolerance":tolerance}

    def combine_shapes_to_tile(self, tile_matrix, cube_size=1.0):
        shapes = []
        for x in range(len(tile_matrix)):
            for y in range(len(tile_matrix[0])):
                if tile_matrix[x][y] == 0:
                    shape = self.generate_square(cube_size=cube_size)
                elif tile_matrix[x][y] == 1:
                    shape = self.generate_square_with_hole(cube_size=cube_size, hole_type="square")
                elif tile_matrix[x][y] == 2:
                    shape = self.generate_square_with_hole(cube_size=cube_size, hole_type="cross")
                elif tile_matrix[x][y] == 3:
                    shape = self.generate_square_with_hole(cube_size=cube_size, hole_type="circle")
                shape["position"] = (cube_size * x, cube_size * y)
                shapes.append(shape)
        return shapes

    def generate_octagon_connection_patches(self, new_radius, new_center, new_center_2, segment, segment_2, start, start_2):
        hole_radius = 1 / (2 * np.cos(np.pi / 8)) * new_radius
        octagon_patches = []
        angles = np.linspace(0, 2 * np.pi, 9)[:-1] + np.pi / 8
        vertices = [(new_center[0] + hole_radius * np.cos(angle), new_center[1] + hole_radius * np.sin(angle)) for angle in angles]
        if start:
            start_point = vertices[segment]
        else:
            start_point = vertices[(segment + 1) % len(vertices)]
        vertices_2 = [(new_center_2[0] + hole_radius * np.cos(angle), new_center_2[1] + hole_radius * np.sin(angle)) for angle in angles]
        if start_2:
            end_point = vertices_2[segment_2]
        else:
            end_point = vertices_2[(segment_2 + 1) % len(vertices_2)]

        path_data = [
            (mpath.Path.MOVETO, start_point),
            (mpath.Path.LINETO, end_point),
        ]
        codes, verts = zip(*path_data)
        path = mpath.Path(verts, codes)
        patch = patches.PathPatch(path, fill=False, color="black")
        octagon_patches.append(patch)

        return octagon_patches

    def generate_octagon_patches(self, new_center, new_radius, draw_segments):
        # Define the octagon parameters
        hole_radius = 1 / (2 * np.cos(np.pi / 8)) * new_radius
        octagon_patches = []

        # Define the vertices of the octagon with flat top and bottom sides
        angles = np.linspace(0, 2 * np.pi, 9)[:-1] + np.pi / 8
        vertices = [(new_center[0] + hole_radius * np.cos(angle), new_center[1] + hole_radius * np.sin(angle)) for angle in angles]

        # Draw each line segment of the octagon
        for i in range(len(vertices)):
            if i in draw_segments:
                start_point = vertices[i]
                end_point = vertices[(i + 1) % len(vertices)]
                path_data = [
                    (mpath.Path.MOVETO, start_point),
                    (mpath.Path.LINETO, end_point),
                ]
                codes, verts = zip(*path_data)
                path = mpath.Path(verts, codes)
                patch = patches.PathPatch(path, fill=False, color="black")
                octagon_patches.append(patch)
        return octagon_patches

    def generate_cross_path(self, position, size, arm_width_ratio=0.3, arm_length_ratio=0.3):
        Path = mpath.Path
        half_size = size / 2
        arm_width = size * arm_width_ratio
        arm_length = size * arm_length_ratio
        position_offset = (position[0] + (1 - size) / 2, position[1] + (1 - size) / 2)
        path_data = [
            (Path.MOVETO, (position_offset[0] + half_size - arm_width / 2, position_offset[1])),
            (Path.LINETO, (position_offset[0] + half_size + arm_width / 2, position_offset[1])),
            (Path.LINETO, (position_offset[0] + half_size + arm_width / 2, position_offset[1] + half_size - arm_length / 2)),
            (Path.LINETO, (position_offset[0] + size, position_offset[1] + half_size - arm_length / 2)),
            (Path.LINETO, (position_offset[0] + size, position_offset[1] + half_size + arm_length / 2)),
            (Path.LINETO, (position_offset[0] + half_size + arm_width / 2, position_offset[1] + half_size + arm_length / 2)),
            (Path.LINETO, (position_offset[0] + half_size + arm_width / 2, position_offset[1] + size)),
            (Path.LINETO, (position_offset[0] + half_size - arm_width / 2, position_offset[1] + size)),
            (Path.LINETO, (position_offset[0] + half_size - arm_width / 2, position_offset[1] + half_size + arm_length / 2)),
            (Path.LINETO, (position_offset[0], position_offset[1] + half_size + arm_length / 2)),
            (Path.LINETO, (position_offset[0], position_offset[1] + half_size - arm_length / 2)),
            (Path.LINETO, (position_offset[0] + half_size - arm_width / 2, position_offset[1] + half_size - arm_length / 2)),
            (Path.CLOSEPOLY, (position_offset[0] + half_size - arm_width / 2, position_offset[1])),
        ]
        codes, verts = zip(*path_data)
        return mpath.Path(verts, codes)

    def generate_smothe_rectangle(self, move_x, move_y, max_x, max_y, corner_radius):
        # Create the path for the rounded rectangle with the move offsets
        Path = mpath.Path
        path_data = [
            (Path.MOVETO, (corner_radius + move_x, move_y)),
            (Path.LINETO, (max_x - corner_radius + move_x, move_y)),
            (Path.CURVE3, (max_x + move_x, move_y)),
            (Path.CURVE3, (max_x + move_x, corner_radius + move_y)),
            (Path.LINETO, (max_x + move_x, max_y - corner_radius + move_y)),
            (Path.CURVE3, (max_x + move_x, max_y + move_y)),
            (Path.CURVE3, (max_x - corner_radius + move_x, max_y + move_y)),
            (Path.LINETO, (corner_radius + move_x, max_y + move_y)),
            (Path.CURVE3, (move_x, max_y + move_y)),
            (Path.CURVE3, (move_x, max_y - corner_radius + move_y)),
            (Path.LINETO, (move_x, corner_radius + move_y)),
            (Path.CURVE3, (move_x, move_y)),
            (Path.CURVE3, (corner_radius + move_x, move_y)),
            (Path.CLOSEPOLY, (corner_radius + move_x, move_y)),
        ]

        codes, verts = zip(*path_data)
        path = mpath.Path(verts, codes)

        # Create the patch and add it to the axis
        patch = patches.PathPatch(path, fill=False, edgecolor="black", linewidth=1)
        return patch


if __name__ == "__main__":
    os.makedirs("test_svg", exist_ok=True)

    svgGenerator = SvgGenerator("test_svg", "test_svg")
    svgGenerator.generate_and_save_riddle_svg([[1, 1, 1], [1, 0, 1], [1, 1, 0]], "test_riddle",tolerance=0)
    svgGenerator.generate_and_save_tile_svg([{"position": [[0, 3, 0], [1, 2, 1], [0, 2, 0], [1, 0, 0]]}], "test_tile", 1)
