#!/usr/bin/env python3
"""Calculate node positions for a given network."""

from glob import glob
import pandas as pd

import networkx as nx


if __name__ == '__main__':
    # VARIABLES
    in_folder = "./networks/"
    out_folder = "./positions/"

    files = glob(in_folder + "*.gexf")

    # COMPUTE
    print(">>> Now working on:")
    for file in files:
        # Read in
        identifier = file.split("/")[-1][:-5]
        print("... {}".format(identifier))
        H = nx.read_gexf(file)

        # Compute positions
        node_positions = nx.nx_agraph.pygraphviz_layout(H, prog="neato")
        s = pd.Series(node_positions, name="positions")
        s.index.name = "node"

        # Write out
        out_file = "{}{}.csv".format(out_folder, identifier)
        s.to_csv(out_file, header=True)
