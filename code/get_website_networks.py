#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Generates js for website to display the networks."""

import csv
import json
from glob import glob
from os.path import basename, splitext
from string import Template

import networkx as nx
from networkx.readwrite import json_graph

from compute_centralities import giant

RANKING_FOLDER = "./centralities/"
NETWORK_FOLDER = "./networks/"
POSITIONS_FOLDER = "./positions/"
TARGET_FOLDER = "../static/"

# Templates
text_tmplte = Template(
    '$name<br>'
    'Thanks: $thanks_v (Rank: $thanks_r)<br>'
    'Betweenness cent. rank: $betw_r<br>'
    'Eigenvector cent. rank: $eig_r')
node_tmplte = Template('{id:$id,label:"$label",title:"$title",'
                       'x:$x,y:$y,value:1,group:"$group"}')
edge_tmplte = Template('{from:$fr,to:$to}')


def compress(d, drops):
    """Remove specified entries from sub-dict."""
    for sd in d:  # Remove enumeration and compress
        for drop in drops:
            sd.pop(drop, None)
    return d


def main():
    for fname in glob(NETWORK_FOLDER + "both*.gexf"):
        # READ IN
        _, year = splitext(basename(fname))[0].split("_")
        H = nx.read_gexf(fname)
        with open("{}both_{}.csv".format(RANKING_FOLDER, year), 'r') as inf:
            ranks = {row.pop("node"): row for row in csv.DictReader(inf)}
        with open("{}both_{}.csv".format(POSITIONS_FOLDER, year), 'r') as inf:
            pos = {row["node"]: (row['x'], row['y']) for row in csv.DictReader(inf)}

        # GENERATE RING VIEW
        ring = json_graph.node_link_data(H)
        drops = ["journal", "year", "jel", "title", "id"]
        ring['links'] = compress(ring['links'], drops)
        with open("{}json/{}-ring.json".format(TARGET_FOLDER, year), 'w') as ouf:
            ouf.write(json.dumps(ring))

        # GENERATE GRAPH VIEW
        # Performs reduction and manual code generation
        G = giant(H)
        # remove edges representing one-time collaboration having weight < 1
        remove = []
        for sourc, tar, data in G.edges(data=True):
            if data["weight"] < 1:
                remove.append((sourc, tar))
        G.remove_edges_from(remove)
        G = giant(G)  # remove single nodes
        G = nx.convert_node_labels_to_integers(G, label_attribute="name")
        # add groups, scaled positions and text
        for node, data in G.nodes(data=True):
            name = data['name']
            # Groups (compressed)
            if data.get("thanks", 0) == 0:
                data["group"] = "a"  # pure author
            elif data.get("papers", 0) == 0:
                data["group"] = "c"  # pure commenter
            else:
                data["group"] = "b"  # commenting author
            # Positions
            x, y = pos[name]
            data["x"] = float(x)*10
            data["y"] = float(y)*10
            # Text
            data['text'] = text_tmplte.substitute(
                name=name, thanks_v=int(data.get("thanks", 0)),
                thanks_r=ranks[name].get("thanks_rank", "-"),
                betw_r=ranks[name]["betweenness_rank"],
                eig_r=ranks[name]["eigenvector_rank"])

        # Write out
        nodes = [node_tmplte.substitute(id=node, label=data["name"],
                                        title=data['text'], x=data["x"],
                                        y=data["y"], group=data["group"])
                 for node, data in G.nodes(data=True)]
        edges = [edge_tmplte.substitute(fr=s, to=t) for s, t in G.edges()]
        out_text = u'var nodes=[{}];\nvar edges=[{}];'.format(
            ','.join(nodes), ','.join(edges))
        with open("{}js/{}-network.js".format(TARGET_FOLDER, year), 'w') as ouf:
            ouf.write(out_text)


if __name__ == '__main__':
    main()
