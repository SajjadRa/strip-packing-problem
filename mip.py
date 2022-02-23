from typing import Tuple

# import gurobipy as grb
from dataclasses import replace

from soring_heuristic import insert_tiles
from main import BIN_WIDTH, Coordinate, Tile, Tiles
from visualisation import visualize


def covered_coordinates(coordinate: Coordinate, tile: Tile) -> Tuple[Coordinate]:
    return tuple(
        Coordinate(x, y)
        for x in range(max(0, coordinate.x - tile.width + 1), coordinate.x + 1)
        for y in range(max(0, coordinate.y - tile.height + 1), coordinate.y + 1)
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
        var_bin_height = spp_model.addVar(
            vtype=grb.GRB.INTEGER, obj=1, name="bin_height"
        )
        var_assignment = spp_model.addVars(
            all_assignment_options,
            vtype=grb.GRB.BINARY,
            name="x_coordinate",
            # obj=[coordinate.y for tile, coordinate in all_assignment_options],
        )

        spp_model.addConstrs(
            var_assignment.sum(tile, "*") == 1 for tile in remaining_tiles
        )
        # overlap constraints
        spp_model.addConstrs(
            grb.quicksum(
                grb.quicksum(
                    var_assignment.get((tile, lb_coordinate), 0)
                    for lb_coordinate in covered_coordinates(coordinate, tile)
                )
                for tile in remaining_tiles
            )
            <= 1
            for coordinate in all_coordinates
        )

        # objective function
        spp_model.addConstrs(
            var_bin_height
            >= (coordinate.y + tile.height) * var_assignment[tile, coordinate]
            for tile, coordinate in all_assignment_options
        )
        spp_model.optimize()

        assigned_grouped_tiles, max_height_per_x = insert_tiles(grouped_tiles)
        grouped_max_height = int(max(max_height_per_x.values()))

        assigned_tiles = list(
            replace(
                tile,
                coordinate=Coordinate(coordinate.x, coordinate.y + grouped_max_height),
            )
            for tile, coordinate in var_assignment.keys()
            if var_assignment[tile, coordinate].X > 0
        )

        final_max_height = int(var_bin_height.X) + grouped_max_height
        print("Max height: " + str(final_max_height))
    if plot:
        visualize(
            BIN_WIDTH,
            final_max_height,
            tuple(assigned_tiles + list(assigned_grouped_tiles)),
        )
    return final_max_height
