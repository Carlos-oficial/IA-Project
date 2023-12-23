from ia.ui.map_generator import MapGenerator
from ia.map.map import Map

s = MapGenerator.run()
print(s)
map = Map.from_map_gen_state(s)
