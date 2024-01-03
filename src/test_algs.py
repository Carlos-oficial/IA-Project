import matplotlib.pyplot as plt
import osmnx as ox

from ia.drivers.driver import Driver
from ia.drivers.veichle import *
from ia.map.map import Map
from ia.map.search import *
from ia.sym import Simulation
from ia.ui.map_generator import MapGenerator, MapGeneratorState

'''
class InteractiveMap:
    def __init__(self):
        self.map_location = None
        self.nodes = set()
        self.nodes_src_dest = set()
        self.restriction = set()
        self.algorithm = None
        self.algorithms_available = {
            "AStar": AStar,
            "BFS": BFS,
            "DFS": DFS,
            "GreedySearch": GreedySearch,
            "UniformCostSearch": UniformCostSearch,
            "TourSearch": TourSearch,
            "RestrictedTourSearch": RestrictedTourSearch,
            "AndOrRestrictedTourSearch": AndOrRestrictedTourSearch,
            "DeliverySearch": DeliverySearch
        }

    def fetch_map(self):
        try:
            self.map_location = input("Digite o nome do mapa: ")
        except Exception as e:
            print(f"Erro ao obter o nome do mapa: {e}")

    def add_nodes(self, map_instance: Map):
        try:
            nodes_input = input("Adicione os nodos separados por vírgula (ex: A,CO,FY,IG,HI): ")
            nodes_string = set(nodes_input.split(','))
            for node in nodes_string:
                self.nodes.add(map_instance.get_node_by_name(node))
            nodes_input1 = input("Agora escolhe o nodo de inicio e de fim (ex: A,HI): ")
            nodes_string1 = set(nodes_input1.split(','))
            for node in nodes_string1:
                self.nodes_src_dest.add(map_instance.get_node_by_name(node))
        except Exception as e:
            print(f"Erro ao adicionar nodos: {e}")

    def choose_algorithm(self):
        try:
            print("Algoritmos clássicos disponíveis:")
            print(", ".join(self.algorithms_available.keys()))
            algorithm_input = input("Digite o nome do algoritmo clássico que deseja na procura: ")
            if algorithm_input in self.algorithms_available:
                self.algorithm = algorithm_input
            else:
                print("Algoritmo não reconhecido. Escolha um dos algoritmos disponíveis.")
                self.choose_algorithm()
        except Exception as e:
            print(f"Erro ao escolher o algoritmo: {e}")

    def run(self, map_instance: Map):
        try:
            if self.algorithm in {"TourSearch", "RestrictedTourSearch", "AndOrRestrictedTourSearch", "DeliverySearch"}:
                node_dest = self.nodes_src_dest.pop() if self.nodes_src_dest else None
                node_src = self.nodes_src_dest.pop() if self.nodes_src_dest else None
                classic_algorithm = input("Digite o nome do algoritmo clássico a ser utilizado: ")
                alg_class = self.algorithms_available.get(classic_algorithm)
                if alg_class:
                    alg = alg_class(map_instance, map_instance.distance)
                else:
                    raise Exception("Algoritmo não encontrado")
                
                #O ERROO ESTA POR AQUI
                algoritmo = self.algorithms_available.get(self.algorithm)
                algoritmo1 = algoritmo(map_instance, map_instance.distance, alg)

                res = algoritmo1.run(node_src, node_dest, self.nodes)
                res.plot()
                print(res)
            else:
                alg_class = self.algorithms_available.get(self.algorithm)
                if alg_class:
                    alg = alg_class(map_instance, map_instance.distance)
                else:
                    raise Exception("Algoritmo não encontrado")
                node_src = self.nodes_src_dest.pop() if self.nodes_src_dest else None
                node_dest = self.nodes_src_dest.pop() if self.nodes_src_dest else None
                res = alg.run(node_src, node_dest, self.nodes)
                res.plot()
                print(res)
            
        except Exception as e:
            print(f"Erro ao executar o programa: {e}")

if __name__ == "__main__":
    interactive_map = InteractiveMap()

    interactive_map.fetch_map()
    map_instance = Map(interactive_map.map_location, "file")
    map_instance.fetch_map()
    map_instance.plot()
    interactive_map.add_nodes(map_instance)
    interactive_map.choose_algorithm()

    interactive_map.run(map_instance)
'''




# s = MapGenerator.run()


map = Map("Gualtar, PT", "file")
map.fetch_map()

A = map.get_node_by_name("A")
CO = map.get_node_by_name("CO")
FY = map.get_node_by_name("FY")
IG = map.get_node_by_name("IG")
HI = map.get_node_by_name("HI")


alg = AStar(map, map.distance)
route_alg = AndOrRestrictedTourSearch(map, map.distance, alg)
route_alg2 = DeliverySearch(map, map.distance, alg)

res = alg.run(IG, CO)
# res1.plot()
# res2 = route_alg2.run(A, IG, {A, HI, (CO, FY)})
# res2.plot()
res.plot()
print(res)
# AA AJ GA GG HI
