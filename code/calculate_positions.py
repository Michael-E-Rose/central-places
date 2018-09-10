#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Calculates node positions for all networks."""

from glob import glob
import pandas as pd

import networkx as nx

SOURCE_FOLDER = "./networks/"
TARGET_FOLDER = "./positions/"


def main():
    print(">>> Now working on:")
    for file in glob(SOURCE_FOLDER + "*.gexf"):
        # Read in
        identifier = file.split("/")[-1][:-5]
        print("... {}".format(identifier))
        H = nx.read_gexf(file)

        # Compute positions
        node_positions = nx.nx_agraph.pygraphviz_layout(H)
        df = pd.DataFrame(node_positions).T
        df.columns = ['x', 'y']
        df.index.name = "node"

        # Write out
        out_file = "{}{}.csv".format(TARGET_FOLDER, identifier)
        df.to_csv(out_file, header=True)


if __name__ == '__main__':
    main()
