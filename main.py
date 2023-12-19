import matplotlib.pyplot as plt
import networkx as nx
from ia.algoritm.a_star import a_star_search

from ia.map.map import Map
from ia.orders.health_planet import HealthPlanet
#from ia.orders.product import Product

mapa = Map.loader("map.json")

enterprise = HealthPlanet(mapa)
start_place = mapa.get_place("Viana do Castelo")  
end_place = mapa.get_place("Aveiro")  

path = a_star_search(mapa,start_place, end_place)
print("Path:", [place.name for place in path])

# Draw the graph
G = mapa.networkx_graph()
pos = nx.spring_layout(G)
nx.draw(
    G,
    pos,
    with_labels=True,
)
plt.savefig("mapa.png")
