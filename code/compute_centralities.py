#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Computes centralities for all nodes for all networks."""

import operator
from glob import glob

import networkx as nx
import pandas as pd

SOURCE_FOLDER = "./networks/"
TARGET_FOLDER = "./centralities/"


def giant(G):
    """Return giant component of a network."""
    components = sorted(nx.connected_component_subgraphs(G),
                        key=len, reverse=True)
    return components[0]


def get_ranks(d):
    """Return a dictionary with ranks as value based on another
    dictionary's values.

    From http://stackoverflow.com/a/2309122/3621464 and
    http://stackoverflow.com/a/613218/3621464
    """
    res = {}
    prev = None
    sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
    for idx, (node, v) in enumerate(sorted_d):
        if v != prev:
            rank = idx + 1
            prev = v
        res[node] = rank
    return res


def main():
    print(">>> Now working on:")
    for file in glob(SOURCE_FOLDER + "*.gexf"):
        # Read in
        identifier = file.split("/")[-1][:-5]
        print("... {}".format(identifier))
        year = identifier.split("-")[-1]
        network = identifier.split("_")[0]

        # Define objects
        H = nx.read_gexf(file)
        G = giant(H)
        df = pd.DataFrame(index=sorted(H.nodes()))

        # number of neighbors (H)
        degree = dict(nx.degree(H))
        df["degree"] = pd.Series(degree)
        df["degree_rank"] = pd.Series(get_ranks(degree)).astype(object)
        # betweenness centrality (G)
        betweenness = dict(nx.betweenness_centrality(G, weight="weight"))
        df["betweenness"] = pd.Series(betweenness)
        df["betweenness_rank"] = pd.Series(get_ranks(betweenness)).astype(object)
        # eigenvector centrality (G) - may fail in small networks
        try:
            eigenvector = dict(nx.eigenvector_centrality(G, weight="weight"))
            df["eigenvector"] = pd.Series(eigenvector)
            df["eigenvector_rank"] = pd.Series(get_ranks(eigenvector)).astype(object)
        except:
            df["eigenvector"] = ""
            df["eigenvector_rank"] = ""
        # number of papers authored or times acknowledged (H)
        if network == "auth":
            attrs = ["papers"]
        elif network == "com":
            attrs = ["thanks"]
        else:
            attrs = ["thanks", "papers"]
        for att_name in attrs:
            attr = nx.get_node_attributes(H, att_name)
            df[att_name] = pd.Series(attr)
            df[att_name + "_rank"] = pd.Series(get_ranks(attr)).astype(object)

        # WRITE OUT
        out_file = "{}{}.csv".format(TARGET_FOLDER, identifier)
        df.to_csv(out_file, index_label="node")


if __name__ == '__main__':
    main()
