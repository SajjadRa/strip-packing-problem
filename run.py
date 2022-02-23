import time

import pandas as pd
from mip import mip_solver
from soring_heuristic import sorted_solver

from main import initialise


def run_series(number_of_tiles: int, solver_method: callable):
    all_results = list()
    for seed in range(100):
        result = dict()

        # sorting_height = min(
        #     sorted_solver(*initialise(number_of_tiles, i, True), plot=False),
        #     sorted_solver(*initialise(number_of_tiles, i, False), plot=False),
        # )
        start_time = time.time()
        grouping_height = solver_method(*initialise(number_of_tiles, seed, True), plot=False)
        result["grouping_time"] = time.time() - start_time

        start_time = time.time()
        optimal_height = solver_method(*initialise(number_of_tiles, seed, False), plot=False)
        result["mip_time"] = time.time() - start_time

        result["optimality_gap"] = 100 * (grouping_height - optimal_height) / optimal_height
        result["optimal_height"] = optimal_height
        # result["sorting_height"] = sorting_height
        result["grouping_height"] = grouping_height
        all_results.append(result)
        pd.DataFrame(all_results).to_csv("all_results_grouping_20.csv")


# seed 4 is not optimal
# 30 and 6 -> mip takes too long
SOLVERS = {"sorter": sorted_solver, "mip": mip_solver}
TO_PLOT = True
NUMBER_OF_TILES = 50
SEED = 0
RUN_IN_SERIES = False
if __name__ == "__main__":
    solver = SOLVERS["sorter"]
    start_time = time.time()
    if RUN_IN_SERIES:
        run_series(NUMBER_OF_TILES, solver)
    else:
        solver(*initialise(NUMBER_OF_TILES, SEED, True), TO_PLOT)

    print(time.time() - start_time)
