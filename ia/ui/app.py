import json
import os
import random
import string
import tkinter as tk
from io import BytesIO
from tkinter import ttk

import geopandas as gpd
import networkx as nx
import osmnx as ox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk


class State:
    def __init__(self):
        self.G = None
        self.gdf = None
        self.selected_nodes = []
        self.location = ""

    def save_to_file(self, fpath):
        os.mkdir(fpath)
        ox.save_graphml(self.G, filepath=fpath + "/osm_graph.graphml")
        with open(fpath + "/data.json", "w") as json_file:
            data = {"location": self.location}
            json.dump(data, json_file, indent=4)


class MapGenerator:
    def __init__(self, master):
        self.master = master
        master.title("Gerar Mapa")

        self.canvas = None
        self.ax = None
        self.fig = None
        self.network_labels = None

        self.state = State()
        # STATe

        # Entry for location
        self.location_entry = tk.Entry(master)
        self.location_entry.grid(row=0)

        # Button to retrieve map
        self.retrieve_button = tk.Button(
            master, text="Retrieve Map", command=self.retrieve_map
        )
        self.retrieve_button.grid(row=1)

        self.points_button = tk.Button(
            master, text="Randomize points", command=self.select_nodes
        )
        self.points_button.grid(row=2)

        self.save_button = tk.Button(master, text="Save", command=self.save)
        self.save_button.grid(row=3)

        self.result_label = tk.Label(self.master, text="")
        self.result_label.grid(padx=20, pady=20)

    def retrieve_map(self):
        try:
            self.state.selected_nodes = []
            # Get location from the entry
            self.state.location = self.location_entry.get()

            g = ox.graph_from_place(self.state.location, network_type="drive")
            self.state.G = g  # ox.get_undirected(g)
            self.state.gdf = ox.features_from_place(
                self.state.location, {"building": True}
            )

            # Plot the graph

            self.draw()

        except Exception as e:
            print(e)
            error_label = ttk.Label(self.master, text=e)
            error_label.grid(row=0, column=0)

    def select_nodes(self):
        try:
            num_points = 10

            # Calculate node centrality measures (e.g., degree centrality)
            centrality = nx.degree_centrality(self.state.G)

            # Get the nodes with highest centrality
            self.state.selected_nodes = random.choices(list(self.state.G), k=10)
            self.master.update_idletasks()
            self.draw()
        except Exception as e:
            print(e)
            error_label = ttk.Label(self.master, text=e)
            error_label.grid(row=0, column=0)

    def save(self):
        # Function to create a new form (Toplevel window)
        form = tk.Toplevel(self.master)
        form.title("Input Form")

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
                print(e)
                error_label = ttk.Label(form, text=e)
                error_label.grid(row=0, column=0)
            # Close the form
            form.destroy()

        # Add a submit button to the form
        submit_button = tk.Button(form, text="Submit", command=submit_form)
        submit_button.grid(pady=20)

    def draw(self):
        self.fig, self.ax = ox.plot_graph(
            self.state.G,
            node_size=0,
            edge_color="w",
            edge_linewidth=0.7,
            show=False,
        )
        # or plot street network and the geospatial features' footprints together
        self.fig, self.ax = ox.plot_graph(
            self.state.G,
            ax=self.ax,
            node_size=0,
            edge_color="w",
            edge_linewidth=0.7,
            show=False,
        )
        self.fig, self.ax = ox.plot_footprints(
            self.state.gdf, ax=self.ax, alpha=0.4, show=False, color="cyan"
        )

        pos = {
            node: (data["x"], data["y"]) for node, data in self.state.G.nodes(data=True)
        }
        nodes = nx.draw_networkx_nodes(
            self.state.G,
            pos=pos,
            nodelist=self.state.selected_nodes,
            node_color="r",
            node_size=50,
        )
        a = list(string.ascii_uppercase)
        i = 0
        for node, data in self.state.G.nodes(data=True):
            if node in self.state.selected_nodes:
                data["pickup"] = a[i % len(a)] + (
                    str(int(i / len(a))) if ((i / len(a)) >= 1) else ""
                )
                i += 1

        node_labels = nx.get_node_attributes(self.state.G, "pickup")
        labels = {
            key: node_labels[key]
            for key in self.state.selected_nodes
            if key in node_labels
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

        if self.canvas is None:
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
            # self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
            self.canvas.get_tk_widget().grid()
        else:
            # Update the existing canvas with the new figure
            self.canvas.figure = self.fig
            self.canvas.draw()

    def run():
        root = tk.Tk()
        app = MapGenerator(root)
        root.mainloop()
