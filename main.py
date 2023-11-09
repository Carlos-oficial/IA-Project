import matplotlib.pyplot as plt
import networkx as nx

from ia.map import Map
from ia.place import Place
from ia.road import Road
from ia.health_planet import HealthPlanet
from ia.product import Product

Braga = Place("Braga")
Guimaraes = Place("Guimarães")
Porto = Place("Porto")
Lisbon = Place("Lisbon")
Coimbra = Place("Coimbra")
Aveiro = Place("Aveiro")
Viseu = Place("Viseu")
Guarda = Place("Guarda")
Faro = Place("Faro")

# Create a map
mapa = Map()

# Add roads to the map
mapa.add_road(Braga, Guimaraes, 20)
mapa.add_road(Guimaraes, Porto, 30)
mapa.add_road(Porto, Lisbon, 280)
mapa.add_road(Braga, Lisbon, 330)
mapa.add_road(Porto, Coimbra, 120)
mapa.add_road(Coimbra, Lisbon, 200)
mapa.add_road(Porto, Aveiro, 90)
mapa.add_road(Aveiro, Lisbon, 250)
mapa.add_road(Braga, Coimbra, 280)
mapa.add_road(Guimaraes, Coimbra, 260)
mapa.add_road(Coimbra, Viseu, 90)
mapa.add_road(Viseu, Guarda, 60)
mapa.add_road(Guarda, Lisbon, 310)
mapa.add_road(Lisbon, Faro, 280)
mapa.add_road(Coimbra, Aveiro, 70)
mapa.add_road(Aveiro, Viseu, 110)
mapa.add_road(Guarda, Viseu, 45)
mapa.add_road(Aveiro, Faro, 410)

enterprise = HealthPlanet(mapa)
enterprise.add_warehouse("Braga", {Product("Arroz", 1.5)})
enterprise.order_product("Faro", "Arroz")
print(enterprise.map.path_length(enterprise.map.calculate_path("Braga", "Porto")))
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
