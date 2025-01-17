import json
from collections import defaultdict
from typing import *

import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
import seaborn as sns

from ia.drivers.driver import Driver
from ia.drivers.veichle import *
from ia.map.map import Map
from ia.map.search import *
from ia.sym import Simulation
from ia.ui.map_generator import MapGenerator, MapGeneratorState


def get_proportion(map: Map, heuristic, n=100):
    """
    computa um estimado da proporção entre distancia real e heursitica
    """
    acc = 0
    s1 = list(map._node_names.keys())

    for i in range(0, n):
        A = random.choice(s1)
        B = random.choice(s1)
        H = heuristic(A, B)
        if H <= 20:
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


if __name__ == "__main__":
    try:
        # n = int(input("test how many? "))
        n = 10000
    except Exception as e:
        "input is not an integer"
    else:
        map = Map("Gualtar, PT", "file")
        map.fetch_map()
        map.factor = 1
        map.factor = get_proportion(map, map.distance, n=10000)
        print("Factor is", map.factor)
        data = test_algorithms(
            map,
            AStar(map, map.distance),
            GreedySearch(map, map.distance),
            UniformCostSearch(map),
            BFS(map),
            DFS(map),
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

        data = proportions

        reshaped_data = []
        for key, value in data.items():
            for algorithm, metrics in value.items():
                reshaped_data.append(
                    {
                        "Node": key,
                        "Algorithm": algorithm,
                        "Relative Path Cost": metrics["relative_path_cost"],
                        "ExploredN/PathN": metrics["exploredN/pathN"],
                    }
                )

        # Create a DataFrame from the reshaped data
        import pandas as pd

        df = pd.DataFrame(reshaped_data)

        # Create box plots using Seaborn
        plt.figure(figsize=(14, 8))
        sns.set_theme(style="whitegrid")
        box_plot = sns.boxplot(x="Algorithm", y="Relative Path Cost", data=df)
        plt.title("Relative Path Cost by Algorithm")
        plt.show()

        plt.figure(figsize=(14, 8))
        sns.set_theme(style="whitegrid")
        box_plot = sns.boxplot(x="Algorithm", y="ExploredN/PathN", data=df)
        plt.title("ExploredN/PathN by Algorithm")
        plt.show()

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

        methods = list(algorithm_averages.keys())
        relative_path_costs = [
            value["relative_path_cost"] for value in algorithm_averages.values()
        ]
        exploredN_pathN = [
            value["exploredN/pathN"] for value in algorithm_averages.values()
        ]

        fig, ax = plt.subplots(figsize=(10, 6))

        bar_width = 0.35
        bar2 = ax.bar(methods, exploredN_pathN, bar_width, label="ExploredN/PathN")
        bar1 = ax.bar(
            methods, relative_path_costs, bar_width, label="Relative Path Cost"
        )

        ax.set_ylabel("Values")
        ax.set_title("A* vs Greedy Search vs Uniform Cost Search vs BFS vs DFS")
        ax.legend()

        plt.show()
