from typing import Tuple, Dict

from main import BIN_WIDTH, Coordinate, Tile, Tiles
from visualisation import visualize


def sorted_solver(remaining_tiles: Tiles, grouped_tiles: Tiles, plot: bool = True):
    sorted_tiles = grouped_tiles + sorted(
        remaining_tiles, key=lambda tile: initial_sorted_key(tile), reverse=True
    )
    assigned_tiles, max_height_per_x = insert_tiles(sorted_tiles)

    final_max_height = int(max(max_height_per_x.values()))
    print("Max height: " + str(final_max_height))

    if plot:
        visualize(BIN_WIDTH, final_max_height, assigned_tiles)

    return final_max_height


def initial_sorted_key(tile: Tile):
    return min(tile.width, BIN_WIDTH - tile.width), tile.width, tile.height
    # return -1 * tile.width, - 1 * tile.height


def insert_tiles(tiles: Tiles) -> Tuple[Tiles, Dict[int, int]]:
    max_height_per_x = {x: 0 for x in range(BIN_WIDTH)}
    assigned_tails = list()
    for tile in tiles:
        x_start = find_best_feasible_x(tile, max_height_per_x)
        highest_y = max(max_height_per_x[x_start + w] for w in range(tile.width))
        assigned_tails.append(tile.replace(coordinate=Coordinate(x_start, highest_y)))
        for w in range(tile.width):
            max_height_per_x[x_start + w] = highest_y + tile.height

    return assigned_tails, max_height_per_x


def find_best_feasible_x(tile: Tile, max_height_per_x) -> int:
    return min(
        range(tile.max_x + 1),
        key=lambda x: key_sort_to_choose_x(x, tile.width, max_height_per_x),
    )


def key_sort_to_choose_x(x: int, width: int, max_height_per_x: Dict[int, int]):
    # fit wide tiles from left, but narrow tiles from right
    if width >= BIN_WIDTH / 2:
        left_or_right = 1
    else:
        left_or_right = -1
    return max_height(x, width, max_height_per_x), left_or_right * x


def max_height(x_start: int, width: int, max_height_per_x: Dict[int, int]) -> int:
    return max(max_height_per_x[x_start + x] for x in range(width))
