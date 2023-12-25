import networkx as nx
import osmnx as ox
from geopy.distance import geodesic


def convert_to_meters(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters


# Replace 'your_place_name' with the desired location or coordinates
place_name = "Gualtar, PT"
graph = ox.graph_from_place(place_name, network_type="all")

# Replace these with the coordinates of your reference point
reference_lat = graph.nodes[list(graph.nodes())[0]]["y"]
reference_lon = graph.nodes[list(graph.nodes())[0]]["x"]
reference_point = (reference_lat, reference_lon)

# Convert node coordinates to meters relative to the reference point
for node, data in graph.nodes(data=True):
    lat, lon = data["y"], data["x"]
    data["distance_to_reference"] = convert_to_meters(
        reference_point[0], reference_point[1], lat, lon
    )

# Print the length of graph edges and their Euclidean distances
for edge in graph.edges(data=True):
    u, v, data = edge
    length = data["length"]
    euclidean_distance = convert_to_meters(
        graph.nodes[u]["y"],
        graph.nodes[u]["x"],
        graph.nodes[v]["y"],
        graph.nodes[v]["x"],
    )

    print(
        f"Edge: ({u}, {v}), Length: {length} meters, Euclidean Distance: {euclidean_distance} meters"
    )
