import random

from matplotlib import patches as patches
from matplotlib import pyplot as plt

from main import Tiles


def visualize(width, height, tiles: Tiles):
    fig = plt.figure(figsize=(width / 2, height / 2))
    axes = fig.add_subplot(1, 1, 1)
    axes.add_patch(
        patches.Rectangle(
            (0, 0),
            width,
            height,
            hatch="x",
            fill=False,
        )
    )
    for tile in tiles:
        axes.add_patch(
            patches.Rectangle(
                (tile.coordinate.x, tile.coordinate.y),
                tile.width,
                tile.height,
                color=(random.random(), random.random(), random.random()),
            )
        )
        axes.text(
            tile.coordinate.x + tile.width / 2,
            tile.coordinate.y + tile.height / 2,
            str(tile),
        )
    axes.set_xlim(0, width)
    axes.set_xticks(range(width + 1))
    axes.set_ylim(0, height)
    axes.set_yticks(range(height + 1))
    plt.gca().set_aspect("equal", adjustable="box")
    plt.savefig("bin.svg")
