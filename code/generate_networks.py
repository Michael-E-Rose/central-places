#!/usr/bin/env python3
"""Generate five undirected weighted networks spanning three years each."""

from collections import Counter
from itertools import combinations, product
from numbers import Number

import networkx as nx
import pandas as pd


def add_edge_attrs(network, edge, attr_dict, sep='; '):
    """Append attributes from attribute dictionary to edges.

    If the attribute is a number, it will be added to the existing attribute.
    If the attribute is a string, it will be added with a separator.
    """
    d = network.edge[edge[0]][edge[1]]
    for key, value in attr_dict.items():
        if key in d.keys():
            if not isinstance(value, Number):
                value = sep + value  # append
            d[key] += value  # increase
        else:
            d[key] = value  # create


def build_network(row):
    """Build weighted undirected network row-wise from dataframe."""
    # Variables
    auths = row['auth']
    coms = row['com'] + row['phd'] + row['dis']
    auth_edges = list(combinations(auths, 2))
    com_edges = list(product(auths, coms))
    attr = {"weight": 1.0, "journal": row['journal']}
    # Update auth network
    G["auth"].add_nodes_from(auths)
    G["auth"].add_edges_from(auth_edges)
    for edge in auth_edges:
        add_edge_attrs(G["auth"], edge, attr)
    # Update com network
    G["com"].add_nodes_from(auths + coms)
    G["com"].add_edges_from(auth_edges)
    for edge in auth_edges:
        add_edge_attrs(G["com"], edge, attr)
    G["com"].add_edges_from(com_edges)
    attr['weight'] = 1.0/len(auths)
    for edge in com_edges:
        add_edge_attrs(G["com"], edge, attr)


if __name__ == '__main__':
    # VARIABLES
    input_file = "../../InformalCollaboration/Code/110_consolidated_acks/acks.csv"
    output_folder = "networks/"

    # yearly 3-year rolling networks
    YEARS = {'1999': range(1997, 1999+1),
             '2002': range(2000, 2002+1),
             '2005': range(2003, 2005+1),
             '2008': range(2006, 2008+1),
             '2011': range(2009, 2011+1)}

    # READ IN
    cols = ["title", "year", "journal", "auth", "com", "phd", "dis"]
    df = pd.read_csv(input_file, index_col=0, usecols=cols)
    df = df.applymap(lambda x: eval(str(x)))
    df['journal'] = df['journal'].apply(lambda x: x[0])
    df['com'] = df['com'].apply(lambda l: [x for x in l
                                if not isinstance(x, (int, float))])

    # GENERATE NETWORKS
    # loop over all specified entries and create subsets
    for year, r in YEARS.items():
        G = {"auth": nx.Graph(name="auth" + year),
             "com": nx.Graph(name="com" + year)}
        # Build subset
        mask = df[['year']].isin(r).all(1)
        subset = df[mask]

        # Update networks in G row-wise
        subset.apply(build_network, axis=1)

        # Add node attributes
        for key, label in [('auth', 'papers'), ('com', 'thanks')]:
            names = [a for l in subset[key] for a in l]
            count = Counter(names)
            nx.set_node_attributes(G[key], label, count)

        # Write out
        for nwname, nw in G.items():
            ouf = "{}/{}_{}.gexf".format(output_folder, nwname, year)
            nx.write_gexf(nw, ouf)
