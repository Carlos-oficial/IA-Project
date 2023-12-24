import matplotlib.pyplot as plt
import networkx as nx
from ia.algoritm.a_star import a_star_search
from ia.algoritm.greedy import greedy_search

from ia.map.map import Map
#from ia.orders.product import Product


mapa = Map.load("map.json")

start_place = mapa.get_place("Viana do Castelo")  
end_place = mapa.get_place("Lisboa")  

path_a = a_star_search(mapa,start_place, end_place)
path = greedy_search(mapa,start_place, end_place)
print("Path A*:", [place.name for place in path_a])
print("Path Greedy:", [place.name for place in path])

# Draw the graph
G = mapa.networkx_graph()
pos = nx.spring_layout(G)
nx.draw(
    G,
    pos,
    with_labels=True,
)
plt.savefig("mapa.png")
