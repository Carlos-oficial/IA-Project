from map import Map  
from place import Place
from road import Road 
import matplotlib.pyplot as plt
import networkx as nx

Braga = Place("Braga")
Guimaraes = Place("Guimarães")

mapa = Map()
mapa.add_road(Braga,Guimaraes,20)

G = mapa.networkx_graph()
# Define a layout
pos = nx.spring_layout(G)

# Draw the graph
nx.draw(G, pos, with_labels=True)
plt.savefig("mapa.png")