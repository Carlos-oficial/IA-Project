import matplotlib.pyplot as plt
import osmnx as ox

from ia.drivers.driver import Driver
from ia.drivers.veichle import *
from ia.map.map import Map
from ia.map.search import *
from ia.sym import Simulation
from ia.ui.map_generator import MapGenerator, MapGeneratorState
import numpy as np
from typing import *
import json
from collections import defaultdict


def get_proportion(map: Map, heuristic, n=100):
    """
    computa um estimado da proporção entre distancia real e heursitica
    """
    acc = 0
    for i in range(0, n):
        A = random.choice(list(map._node_names.keys()))
        B = random.choice(list(map._node_names.keys()))

        H = heuristic(A, B)
        if H == 0:
            continue
        alg = AStar(map, heuristic)
        res = alg.run(A, B, reset=True)
        len = map.path_length(res.path)
        acc += len / H
        # print(len,H,len/H)
    return acc / n


def test_algorithms(map: Map, *algs: ClassicalSearch, n=100):
    acc = 0
    results: Dict[Any, List[SearchResult]] = dict()
    for i in range(0, n):
        A = random.choice(list(map._node_names.keys()))
        B = random.choice(list(map._node_names.keys()))
        if A == B:
            continue
        for alg in algs:
            res = alg.run(A, B, reset=True)
            d = results.get(str((A, B)))
            if not d:
                d = dict()
                results[str((A, B))] = d
            condensed_res = res.condense(map.path_length)
            try:
                condensed_res["optimal"] = alg.__class__.OPTIMAL
            except Exception as e:
                pass
            d[alg.__str__()] = condensed_res
    return results


# map.proportion = get_proportion(map, map.distance, n=5000)
# print("Proportion is", map.proportion)
if __name__ == "__main__":
    try:
        n = int(input("test how many? "))
    except Exception as e:
        "input is not an integer"
    else:
        map = Map("Gualtar, PT", "file")
        map.fetch_map()
        data = test_algorithms(
            map,
            AStar(map, map.distance),
            GreedySearch(map, map.distance),
            UniformCostSearch(map),
            n=n,
        )
        # print(json.dumps(data, indent=2))
        algs = list(data.values())[0]
        for name, alg in algs.items():
            if alg["optimal"]:
                optimal = name

        proportions = dict()
        for node_pair, algs in data.items():
            for alg_name, alg_results in algs.items():
                if not proportions.get(node_pair):
                    proportions[node_pair] = dict()
                proportions[node_pair][alg_name] = {
                    "relative_path_cost": alg_results["path_cost"]
                    / algs[optimal]["path_cost"],
                    "exploredN/pathN": alg_results["explored_n"]
                    / alg_results["path_n"],
                }
        # print(json.dumps(proportions,indent=2))«

        algorithm_sums = defaultdict(
            lambda: {"relative_path_cost": 0, "exploredN/pathN": 0}
        )

        # Count of instances for each algorithm
        algorithm_counts = defaultdict(lambda: 0)

        # Iterate through the data and calculate the sum for each algorithm
        for node, algorithms in proportions.items():
            for algorithm, metrics in algorithms.items():
                algorithm_sums[algorithm]["relative_path_cost"] += metrics[
                    "relative_path_cost"
                ]
                algorithm_sums[algorithm]["exploredN/pathN"] += metrics[
                    "exploredN/pathN"
                ]
                algorithm_counts[algorithm] += 1

        # Calculate averages for each algorithm
        algorithm_averages = {
            algorithm: {
                "relative_path_cost": sum_metrics["relative_path_cost"] / count,
                "exploredN/pathN": sum_metrics["exploredN/pathN"] / count,
            }
            for algorithm, count in algorithm_counts.items()
            for sum_metrics in [algorithm_sums[algorithm]]
        }

        # Print the results
        for algorithm, averages in algorithm_averages.items():
            print(f"{algorithm}: \n\t {averages}")
