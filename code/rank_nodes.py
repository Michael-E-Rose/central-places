#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Generates html for website to display the network rankings."""

from glob import glob
from os.path import basename, splitext

import networkx as nx
import pandas as pd

SOURCE_FOLDER = "./networks/"
TARGET_FOLDER = "../templates/rankings/"

pd.set_option('display.max_colwidth', None)


def linkfy(name, y):
    """Return link for ring view."""
    label = name.replace(" ", "_").replace("'", "")
    s = u"<a href=\"{{url_for('rings',year='%s',focus='%s')}}\">%s</a>" % (y, label, name)
    return s


def giant(H):
    """Return giant component of a network."""
    components = nx.weakly_connected_components(H)
    return H.subgraph(sorted(components, key=len, reverse=True)[0])


def main():
    for file in sorted(glob(SOURCE_FOLDER + "*.gexf")):
        # Read in
        year = basename(splitext(file)[0])
        H = nx.read_gexf(file)
        G = giant(H)
        df = pd.DataFrame(index=sorted(H.nodes()))

        # Get values
        df["betweenness"] = pd.Series(
            nx.betweenness_centrality(G.to_undirected(), weight="weight"))
        df["eigenvector"] = pd.Series(
            nx.eigenvector_centrality_numpy(G, weight="weight"))
        df["thanks"] = pd.Series(nx.get_node_attributes(H, "thanks"))
        for c in df.columns:
            df[c + "_rank"] = df[c].rank(method="min", ascending=False)

        # Create column with links
        names = nx.get_node_attributes(H, "label")
        df['Name'] = pd.Series(names)
        df['Name'] = df['Name'].apply(lambda x: linkfy(x, year))

        # Sort and write out
        measures = ["thanks", "eigenvector", "betweenness", ]
        for measure in measures:
            rank_meas = measure + '_rank'
            temp = (df.dropna(subset=[measure])
                      .sort_values([rank_meas, 'Name'])
                      .rename(columns={rank_meas: 'Rank', measure: 'Value'}))
            temp['Rank'] = (temp['Rank'].fillna("-").astype(str)
                                        .apply(lambda x: x.split('.')[0]))
            if measure in ('thanks', 'papers'):
                temp['Value'] = temp['Value'].astype(int)
            output_file = f'{TARGET_FOLDER}{year}_{measure}.html'
            order = ['Rank', 'Name', 'Value']
            temp[order].to_html(output_file, index=False, escape=False,
                                classes="table table-hover", na_rep="",
                                float_format=lambda x: '%10.3f' % x)


if __name__ == '__main__':
    main()
