import matplotlib.pyplot as plt
import networkx as nx

from ia.map import Map
from ia.health_planet import HealthPlanet
from ia.product import Product

mapa = Map.loader("data.json")

enterprise = HealthPlanet(mapa)
#enterprise.add_warehouse("Braga", {Product("Arroz", 1.5)})
#enterprise.order_product("Faro", "Arroz")
print(enterprise.map.path_length(enterprise.map.calculate_path("Viana do Castelo", "Faro")))
print(enterprise.map.calculate_path("Viana do Castelo", "Faro"))
# # Define a layout
# for k,v in nx.get_edge_attributes(G, "road").items():
#     v.open = not v.open

# for k,v in nx.get_edge_attributes(G, "road").items():
#     print(k,":",v.__dict__)

# Draw the graph
G = mapa.networkx_graph()
pos = nx.spring_layout(G)
nx.draw(
    G,
    pos,
    with_labels=True,
)
plt.savefig("mapa.png")
