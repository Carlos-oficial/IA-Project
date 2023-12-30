import json
import os
import random
import string
import tkinter as tk
import traceback
from io import BytesIO
from tkinter import ttk

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from scipy.spatial import cKDTree
from sklearn.cluster import KMeans

from ia.orders.products import Product, Warehouse


def hilbert_curve(width, height, num_points):
    t = np.arange(0, num_points, dtype=np.float32) / num_points
    x = np.mod(np.floor(t * width), width)
    y = np.floor(t * height / width)
    indices = np.argsort(np.argsort(x + y * width))
    return np.column_stack((x[indices], y[indices]))


def distribute_nodes_evenly(coords_dict, num_nodes, w, h):
    coordinates = np.array(list(coords_dict.keys()))
    hilbert_points = hilbert_curve(w, h, num_nodes)
    print("hilbert_points:", hilbert_points)
    kdtree = cKDTree(coordinates)
    _, indices = kdtree.query(hilbert_points)

    result = {
        tuple(hilbert_points[i]): list(coords_dict.keys())[indices[i]]
        for i in range(num_nodes)
    }
    return result


def calculate_graph_dimensions(coords):
    """
    Calculate the width and height of a graph using its coordinates.

    Parameters:
    - coords_map: Dictionary mapping nodes to (x, y) coordinates.

    Returns:
    - Tuple containing the width and height of the graph.
    """
    x_values = [x for (x, _) in coords]
    y_values = [y for (_, y) in coords]
    width = max(x_values) - min(x_values)
    height = max(y_values) - min(y_values)
    return width, height


class MapGeneratorState:
    _id = 0

    def __init__(self):
        self.G: nx.MultiDiGraph = None
        self.gdf: gpd.GeoDataFrame = None
        self.selected_nodes = dict({})
        self.location = ""
        self.path = ""
        self.warehouses = Warehouse.read_warehouses_from_json("aramazens.json")
        self.warehouse_nodes = dict()

    def save_to_file(self, fpath):
        self.path = fpath
        os.mkdir(fpath)
        for node, data in self.G.nodes(data=True):
            if node in self.warehouse_nodes.keys():
                data["pickup"] = self.warehouse_nodes[node]
        ox.save_graphml(self.G, filepath=fpath + "/osm_graph.graphml")
        with open(fpath + "/data.json", "w") as json_file:
            data = {
                "location": self.location,
                "warehouses": [w.to_dict() for w in self.warehouses],
            }
            json.dump(data, json_file, indent=4)

    @staticmethod
    def load_from_file(fpath):
        state = MapGeneratorState()
        data_json_path = os.path.join(fpath, "data.json")
        with open(data_json_path, "r") as json_file:
            data = json.load(json_file)

            # Set attributes from the loaded data
            state.location = data["location"]
            state.warehouses = [Warehouse.from_dict(w) for w in data["warehouses"]]

        # Load graph
        graphml_path = os.path.join(fpath, "osm_graph.graphml")
        state.G = ox.load_graphml(graphml_path)
        state.gdf = ox.features_from_place(
            state.location, {"building": True, "highway": True}
        )
        # Load data.json

        # Update warehouse nodes
        state.warehouse_nodes = {}
        for node, data in state.G.nodes(data=True):
            if "pickup" in data:
                state.warehouse_nodes[node] = data["pickup"]

        # Update path
        state.path = fpath

        return state

    @staticmethod
    def new_unique_name():
        def number_to_letters(n):
            result = ""
            while n >= 0:
                result = chr(n % 26 + 65) + result
                n = n // 26 - 1
            return result

        i = MapGeneratorState._id
        MapGeneratorState._id += 1
        return number_to_letters(i)

    @staticmethod
    def retrieve_map(place_name):
        # Get location from the entry

        g = ox.graph_from_place(place_name, network_type="drive")
        # self.state.gdf = ox.features_from_place(
        #     self.state.location, {"building": True, "highway": True}
        # )
        for node, data in g.nodes(data=True):
            data["name"] = MapGeneratorState.new_unique_name()
        return g


class MapGenerator:
    def __init__(self, master):
        self.master = master
        master.title("Gerar Mapa")

        self.canvas = None
        self.ax = None
        self.fig = None
        self.network_labels = None
        self.show_streets = False
        self.state = MapGeneratorState()

        self.setup_ui()

        # STATe

    def setup_ui(self):
        # Entry for location
        self.location_entry = tk.Entry(self.master)
        self.location_entry.focus()
        self.location_entry.grid(row=0, column=0)
        self.location_entry.bind("<Return>", lambda event: self.retrieve_map())

        # Button to retrieve map
        self.retrieve_button = tk.Button(
            self.master, text="Retrieve Map", command=self.retrieve_map
        )
        self.retrieve_button.grid(row=0, column=1)

        toggle_button = tk.Button(
            self.master, text="Toggle street names", command=self.toggle_streets
        )
        toggle_button.grid(row=0, column=2)

        self.points_button = tk.Button(
            self.master, text="Randomize points", command=self.select_nodes
        )
        self.points_button.grid(row=2, column=0)

        self.name_nodes_button = tk.Button(
            self.master, text="Name points", command=self.name_nodes
        )
        self.name_nodes_button.grid(row=2, column=1)

        self.save_button = tk.Button(self.master, text="Save", command=self.save)
        self.save_button.grid(row=3)

        self.result_label = tk.Label(self.master, text="")
        self.result_label.grid(padx=20, pady=20)

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_streets(self):
        self.show_streets = not self.show_streets
        self.draw()

    def retrieve_map(self, where="gualtar"):
        try:
            self.state.selected_nodes = dict({})
            # Get location from the entry
            self.state.location = self.location_entry.get()

            g = ox.graph_from_place(self.state.location, network_type="drive")
            self.state.G = g  # ox.get_undirected(g)
            self.state.gdf = ox.features_from_place(
                self.state.location, {"building": True, "highway": True}
            )
            for node, data in self.state.G.nodes(data=True):
                data["name"] = MapGeneratorState.new_unique_name()

            # Plot the graph

            self.draw()

        except Exception as e:
            traceback.print_exc()
            print(e)
            error_label = ttk.Label(self.master, text=e)
            error_label.grid(row=10, column=0, sticky="w")

    def select_nodes(self):
        try:
            num_points = 10

            self.state.selected_nodes = dict()
            for a, (node, data) in zip(
                self.state.warehouses,
                random.choices(
                    list(dict(self.state.G.nodes(data=True)).items()),
                    k=len(self.state.warehouses),
                ),
            ):
                self.state.selected_nodes[node] = a.name
                self.state.warehouse_nodes[node] = a.name
            self.master.update_idletasks()
            self.draw()
        except Exception as e:
            traceback.print_exc()
            error_label = ttk.Label(self.master, text=e)
            error_label.grid(row=0, column=0)

    def name_nodes(self):
        form = tk.Toplevel(self.master)
        form.title("Rename Nodes")
        labels = dict({})
        entries = dict({})
        for node, name in self.state.selected_nodes.items():
            labels[node] = tk.Label(form, text=name)
            labels[node].grid(padx=20, pady=5)
            entries[node] = tk.Entry(form)
            entries[node].grid(padx=20, pady=5)

        # Function to handle form submission
        def submit_form():
            for node, entry in entries.items():
                val = entry.get()
                if val:
                    self.state.selected_nodes[node] = val
            self.update_node_names()
            # Close the form
            form.destroy()
            self.draw()

        # Add a submit button to the form
        submit_button = tk.Button(form, text="Submit", command=submit_form)
        submit_button.grid(pady=20)

    def update_node_names(self):
        pos = {
            node: (data["x"], data["y"]) for node, data in self.state.G.nodes(data=True)
        }
        nodes = nx.draw_networkx_nodes(
            self.state.G,
            pos=pos,
            nodelist=self.state.selected_nodes.keys(),
            node_color="r",
            node_size=50,
        )
        for node, data in self.state.G.nodes(data=True):
            if node in self.state.selected_nodes.keys():
                data["pickup"] = self.state.selected_nodes[node]

    def save(self):
        # Function to create a new form (Toplevel window)
        form = tk.Toplevel(self.master)
        form.title("Save")

        # Add entry widgets to the form
        label_fpath = tk.Label(form, text="where to save?")
        label_fpath.grid(padx=20, pady=5)
        entry_fpath = tk.Entry(form)
        entry_fpath.grid(padx=20, pady=5)

        # Function to handle form submission
        def submit_form():
            # Get values from entry widgets
            filepath = entry_fpath.get()
            try:
                self.state.save_to_file(filepath)
            except Exception as e:
                traceback.print_exc()

                print(e)
                error_label = ttk.Label(form, text=e)
                error_label.grid(row=0, column=0)
            # Close the form
            form.destroy()

        # Add a submit button to the form
        submit_button = tk.Button(form, text="Submit", command=submit_form)
        submit_button.grid(pady=20)

    def draw(self):
        # plt.cla()
        # plt.clf()
        if self.state.G is not None and self.state.gdf is not None:
            # or plot street network and the geospatial features' footprints together
            self.fig, self.ax = ox.plot_graph(
                self.state.G,
                node_size=0,
                edge_color="w",
                edge_linewidth=0.7,
                show=False,
            )
            self.fig, self.ax = ox.plot_footprints(
                self.state.gdf, ax=self.ax, alpha=0.4, show=False, color="cyan"
            )

            self.update_node_names()

            node_labels = nx.get_node_attributes(self.state.G, "pickup")
            labels = {
                key: node_labels[key]
                for key in self.state.selected_nodes.keys()
                if key in node_labels
            }

            pos = {
                node: (data["x"], data["y"])
                for node, data in self.state.G.nodes(data=True)
            }

            self.network_lables = nx.draw_networkx_labels(
                self.state.G,
                pos,
                labels=labels,
                font_color="white",
                font_size=10,
                font_weight="bold",
                horizontalalignment="right",
                verticalalignment="bottom",
            )

            if self.show_streets:
                # Annotate streets with their names
                for _, row in self.state.gdf.iterrows():
                    # print(row['name'])
                    not_allowed = {"nan"}
                    if str(row["name"]) not in not_allowed:
                        not_allowed.add(row["name"])
                        self.ax.text(
                            row["geometry"].centroid.x,
                            row["geometry"].centroid.y,
                            row["name"],
                            color="red",
                            fontsize=8,
                        )

            if self.canvas is None:
                self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
                self.canvas.get_tk_widget().grid()
            else:
                # Update the existing canvas with the new figure
                self.canvas.figure = self.fig
                self.canvas.draw()

    def on_close(self):
        # Perform any cleanup or additional actions before closing the app
        print("Closing the app...")
        # plt.cla()
        # plt.clf()
        self.master.destroy()
        self.master.quit()
        print("Closed the app.")

    def run():
        root = tk.Tk()
        app = MapGenerator(root)
        root.mainloop()
        return app.state


if __name__ == "__main__":
    print("HI!!!!")
