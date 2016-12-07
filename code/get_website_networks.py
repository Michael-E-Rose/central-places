#!/usr/bin/env python3
"""Generate js for website to display the network."""

import csv
import json
from string import Template

import networkx as nx
from networkx.readwrite import json_graph


def compress(d, drops):
    """Remove specified entries from sub-dict."""
    for sd in d:  # Remove enumeration and compress
        for drop in drops:
            sd.pop(drop, None)
    return d


def giant(G):
    """Return giant component of a network."""
    components = sorted(nx.connected_component_subgraphs(G),
                        key=len, reverse=True)
    return components[0]


def replace_enumeration(d, mapping):
    """Replace enumeration of node ids."""
    for sd in d:
        sd['source'] = mapping[sd['source']]
        sd['target'] = mapping[sd['target']]
    return d


if __name__ == '__main__':
    # VARIABLES
    ranking_folder = "centralities"
    network_folder = "networks"
    positions_folder = "positions"
    output_folder = "../static/"

    YEARS = ['2011', '2008', '2005', '2002', '1999']

    # Templates
    text_tmplte = Template(
        '$name<br>'
        'Number of acknowledgements: $thanks_v (Rank: $thanks_r)<br>'
        'Betweenness centrality rank: $betw_r<br>'
        'Eigenvector centrality rank: $eig_r')
    node_tmplte = Template('{id:$id,label:"$label",title:"$title",'
                           'x:$x,y:$y,value:1,group:"$group"}')
    edge_tmplte = Template('{from:$fr,to:$to}')

    for y in YEARS:
        # READ IN
        ranking_file = "{}/com_{}.csv".format(ranking_folder, y)
        network_file = "{}/com_{}.gexf" .format(network_folder, y)
        positions_file = "{}/com_{}.csv".format(positions_folder, y)
        output_file = {'graph': "{}js/{}-network.js".format(output_folder, y),
                       'ring': "{}json/{}-ring.json".format(output_folder, y)}

        with open(ranking_file, 'r') as inf:
            reader = csv.DictReader(inf)
            ranks = {row.pop("node"): row for row in reader}
        with open(positions_file, 'r') as inf:
            reader = csv.DictReader(inf)
            pos = {row["node"]: eval(row['positions']) for row in reader}

        # GENERATE RING VIEW
        H = nx.read_gexf(network_file)
        id_mapping = {}  # needed to replace numeric id's in json object
        for idx, (node, data) in enumerate(H.nodes(data=True)):
            id_mapping[idx] = node
            data["thanks"] = data.get("thanks", 0)

        # Write out
        ring = json_graph.node_link_data(H)
        drops = ["journal", "year", "jel", "title", "id"]
        ring['links'] = compress(ring['links'], drops)
        ring['links'] = replace_enumeration(ring['links'], id_mapping)
        with open(output_file["ring"], 'w') as ouf:
            ouf.write(json.dumps(ring))

        # GENERATE GRAPH VIEW
        # Performs reduction and manual code generation
        G = giant(H)
        # remove edges representing one-time collaboration having weight < 1
        for sourc, tar, data in G.edges(data=True):
            if data["weight"] < 1 and len(data['journal'].split(";")) == 1:
                G.remove_edge(sourc, tar)
        G = giant(G)  # remove solo nodes
        G = nx.convert_node_labels_to_integers(G, label_attribute="name")
        # add groups, scaled positions and text
        for node, data in G.nodes(data=True):
            name = data['name']
            # Groups (compressed)
            if data["thanks"] == 0:
                data["group"] = "a"  # pure author
            elif 'papers' not in data:
                data["group"] = "c"  # pure commenter
            else:
                data["group"] = "b"  # commenting author
            # Positions
            x, y = pos[name]
            data["x"] = x*10
            data["y"] = y*10
            # Text
            data['text'] = text_tmplte.substitute(
                name=name, thanks_v=data["thanks"],
                thanks_r=ranks[name]["thanks_rank"],
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
        with open(output_file['graph'], 'w') as ouf:
            ouf.write(out_text)
