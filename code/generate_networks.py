#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Generates five undirected weighted networks spanning three years each."""

from collections import defaultdict
from glob import glob
from itertools import combinations, product
from json import loads
from os.path import basename, splitext
from urllib.request import urlopen

import networkx as nx
import pandas as pd

ACK_FILE = "https://cdn.rawgit.com/Michael-E-Rose/CoFE/master/acks_min.json"
EDITOR_FILE = "./editor_tenures/list.csv"
TARGET_FOLDER = "networks/"

SPAN = 3  # yearly 3-year rolling networks


def add_attribute(network, items, val, attr='weight'):
    """Creates, appends or increases attribute of edges or nodes."""
    for entry in items:
        try:  # edge
            d = network.edges[entry[0], entry[1]]
        except KeyError:  # node
            d = network.node[entry]
        try:
            if isinstance(d[attr], str):
                d[attr] += ";" + val  # append
            else:
                d[attr] += val  # increase
        except KeyError:
            d[attr] = val  # create


def main():
    # READ IN
    # List of editors to be removed
    editors = pd.read_csv(EDITOR_FILE).dropna(subset=['scopus_id'])
    editors = editors[editors['managing_editor'] == 1]
    editors['scopus_id'] = editors['scopus_id'].astype(int).astype(str)
    # Acknowlegement data
    data = loads(urlopen(ACK_FILE).read().decode("utf-8"))['data']

    # GENERATE NETWORKS
    A = defaultdict(lambda: nx.Graph())  # authors
    B = defaultdict(lambda: nx.Graph())  # authors and commenters
    C = defaultdict(lambda: nx.Graph())  # commenters
    for item in data:
        pub_year = item['year']
        # Get editors to remove
        editor_range = range(pub_year-1, pub_year+1)  # This year and the one before
        mask = (editors['year'].isin(editor_range)) & (editors['journal'] == item['journal'])
        cur_editors = set(editors[mask]['scopus_id'])
        # Authors
        auths = [a['label'] for a in item['authors']]
        auths = [a.replace("*", "") for a in auths]
        num_auth = len(auths)
        # Commenters
        coms = [c['label'] for c in item.get('com', [])]
        coms.extend([c['label'] for c in item.get('dis', [])])
        coms.extend([p['label'] for x in item['authors']
                     for p in x.get('phd', [])])
        coms = [c.replace("*", "") for c in coms]
        coms = set(coms) - cur_editors
        # Add weighted links to this and the next SPAN networks
        for cur_year in range(pub_year, pub_year+SPAN):
            if cur_year < 1997+SPAN-1 or cur_year > 2011:
                continue
            auth_links = list(combinations(auths, 2))
            com_links = list(product(coms, auths))
            # Author network
            A[cur_year].add_nodes_from(auths)
            A[cur_year].add_edges_from(auth_links)
            add_attribute(A[cur_year], auth_links, 1.0, 'weight')
            add_attribute(A[cur_year], auths, 1.0, 'papers')
            # Commenter network
            C[cur_year].add_nodes_from(coms)
            C[cur_year].add_edges_from(com_links)
            add_attribute(C[cur_year], com_links, 1.0, 'weight')
            add_attribute(C[cur_year], coms, 1.0, 'thanks')
            # Both network
            B[cur_year].add_nodes_from(auths)
            B[cur_year].add_nodes_from(coms)
            B[cur_year].add_edges_from(auth_links)
            add_attribute(B[cur_year], auth_links, 1.0, 'weight')
            add_attribute(B[cur_year], auths, 1.0, 'papers')
            B[cur_year].add_edges_from(com_links)
            add_attribute(B[cur_year], com_links, 1.0/len(auths), 'weight')
            add_attribute(B[cur_year], coms, 1.0, 'thanks')

    # WRITE OUT
    for label, dict in [('auth', A), ('both', B), ('com', C)]:
        for year, G in dict.items():
            ouf = "{}/{}_{}.gexf".format(TARGET_FOLDER, label, year)
            nx.write_gexf(G, ouf)


if __name__ == '__main__':
    main()
