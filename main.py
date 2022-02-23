import itertools
import random
from dataclasses import dataclass, replace
from random import randint
from typing import Collection, Iterable, Tuple

BIN_WIDTH = 6


@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int

    replace = replace


Coordinates = Collection[Coordinate]


@dataclass(frozen=True, repr=False)
class Tile:
    id: int
    width: int
    height: int
    coordinate: Coordinate

    replace = replace

    def __repr__(self):
        return str(self.id)

    def __hash__(self):
        return hash(self.id)

    @property
    def max_x(self) -> int:
        return BIN_WIDTH - self.width

    @property
    def feasible_xs(self) -> Iterable[int]:
        if self.width > BIN_WIDTH / 2:
            return {0}
        else:
            return set(range(BIN_WIDTH - self.width + 1))


Tiles = Iterable[Tile]


def create_random_tile(tile_id: int) -> Tile:
    return Tile(
        id=tile_id,
        width=randint(1, 5),
        height=randint(1, 5),
        coordinate=Coordinate(0, 0),
    )


def initialise(number_of_tiles: int, seed: float, grouped: bool = True) -> Tuple[Tiles, Tiles]:
    random.seed(seed)
    tiles = tuple(create_random_tile(tile_id) for tile_id in range(1, number_of_tiles + 1))
    if grouped:
        return fill_until_match(tiles)
    else:
        return tiles, list()


def fill_until_match(tiles: Tiles) -> Tuple[Tiles, Tiles]:
    listed_tiles = []
    full_width_tiles = {tile for tile in tiles if tile.width == BIN_WIDTH}
    groups_by_width = {
        width: list(group)
        for width, group in itertools.groupby(
            sorted(
                set(tiles) - full_width_tiles,
                key=lambda tile: (tile.width, tile.height),
                reverse=True,
            ),
            key=lambda tile: tile.width,
        )
    }
    listed_tiles += list(full_width_tiles)
    sum_heights = {
        width: sum(tile.height for tile in tiles) for width, tiles in groups_by_width.items()
    }
    for width in [5, 4]:
        if (width in sum_heights.keys()) and (BIN_WIDTH - width in sum_heights.keys()):
            while sum_heights[width] * sum_heights[BIN_WIDTH - width] > 0:
                if sum_heights[width] == sum_heights[BIN_WIDTH - width]:
                    listed_tiles += groups_by_width[width]
                    listed_tiles += groups_by_width[BIN_WIDTH - width]
                    break
                elif sum_heights[width] < sum_heights[BIN_WIDTH - width]:
                    (
                        groups_by_width[BIN_WIDTH - width],
                        sum_heights[BIN_WIDTH - width],
                    ) = remove_extra_tile(
                        groups_by_width[BIN_WIDTH - width],
                        sum_heights[BIN_WIDTH - width],
                        sum_heights[BIN_WIDTH - width] - sum_heights[width],
                    )
                else:
                    groups_by_width[width], sum_heights[width] = remove_extra_tile(
                        groups_by_width[width],
                        sum_heights[width],
                        sum_heights[width] - sum_heights[BIN_WIDTH - width],
                    )

    return set(tiles) - set(listed_tiles), listed_tiles


def remove_extra_tile(tiles: Tiles, sum_heights: int, diff):
    tile_to_remove = sorted(tiles, key=lambda tile: (abs(tile.height - diff), tile.height))[0]
    sum_heights -= tile_to_remove.height
    tiles.remove(tile_to_remove)

    return tiles, sum_heights
