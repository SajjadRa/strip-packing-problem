# import gurobipy as grb
from dataclasses import replace
from typing import Collection, Mapping, Tuple

from soring_heuristic import insert_tiles
from visualisation import visualize

from main import BIN_WIDTH, Coordinate, Coordinates, Tile, Tiles

AssignmentOption = Tuple[Tile, Coordinate]
AssignmentOptions = Collection[AssignmentOption]


class Variables:
    bin_height: grb.Var
    assignment: Mapping[AssignmentOption, grb.Var]

    def __init__(self, model, assignment_options):
        self.bin_height = model.addVar(vtype=grb.GRB.INTEGER, obj=1, name="bin_height")
        self.assignment = model.addVars(
            assignment_options,
            vtype=grb.GRB.BINARY,
            name="x_coordinate",
            # obj=[coordinate.y for tile, coordinate in all_assignment_options],
        )


def mip_solver(remaining_tiles: Tiles, grouped_tiles: Tiles, plot: bool = True):
    height_upperbound = sum(tile.height for tile in remaining_tiles)
    all_coordinates = tuple(
        Coordinate(x, y) for x in range(BIN_WIDTH) for y in range(height_upperbound)
    )
    all_assignment_options = tuple(
        (tile, coordinate)
        for tile in remaining_tiles
        for coordinate in all_coordinates
        if coordinate.x in tile.feasible_xs
    )
    with grb.Env() as env_grb, grb.Model(env=env_grb) as spp_model:
        spp_model.modelSense = grb.GRB.MINIMIZE
        variables = Variables(spp_model, all_assignment_options)

        # Constraints:
        spp_model.addConstrs(variables.assignment.sum(tile, "*") == 1 for tile in remaining_tiles)
        add_overlap_constraints(spp_model, variables, remaining_tiles, all_coordinates)

        add_objective_function(spp_model, variables, all_assignment_options)
        spp_model.optimize()

        assigned_tiles, grouped_max_height = create_optimal_assigned_tiles(grouped_tiles, variables)

        final_max_height = int(variables.bin_height.X) + grouped_max_height
        print("Max height: " + str(final_max_height))
    if plot:
        visualize(
            BIN_WIDTH,
            final_max_height,
            assigned_tiles,
        )
    return final_max_height


def create_optimal_assigned_tiles(grouped_tiles: Tiles, variables: Variables) -> Tuple[Tiles, int]:
    assigned_grouped_tiles, max_height_per_x = insert_tiles(grouped_tiles)
    grouped_max_height = int(max(max_height_per_x.values()))
    assigned_tiles = list(
        replace(
            tile,
            coordinate=Coordinate(coordinate.x, coordinate.y + grouped_max_height),
        )
        for tile, coordinate in variables.assignment.keys()
        if variables.assignment[tile, coordinate].X > 0
    )
    return assigned_grouped_tiles + assigned_tiles, grouped_max_height


def add_objective_function(
    model: grb.Model, variables: Variables, assignment_options: AssignmentOptions
):
    model.addConstrs(
        variables.bin_height
        >= (coordinate.y + tile.height) * variables.assignment[tile, coordinate]
        for tile, coordinate in assignment_options
    )


def add_overlap_constraints(
    model: grb.Model, variables: Variables, tiles: Tiles, coordinates: Coordinates
):
    model.addConstrs(
        grb.quicksum(
            grb.quicksum(
                variables.assignment.get((tile, lb_coordinate), 0)
                for lb_coordinate in covered_coordinates(coordinate, tile)
            )
            for tile in tiles
        )
        <= 1
        for coordinate in coordinates
    )


def covered_coordinates(coordinate: Coordinate, tile: Tile) -> Coordinates:
    return tuple(
        Coordinate(x, y)
        for x in range(max(0, coordinate.x - tile.width + 1), coordinate.x + 1)
        for y in range(max(0, coordinate.y - tile.height + 1), coordinate.y + 1)
    )
