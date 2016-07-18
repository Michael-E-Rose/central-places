#!/usr/bin/env python2.7
"""Generate html for website to display the network rankings."""

import sys
from itertools import product

import pandas as pd

reload(sys)
sys.setdefaultencoding('utf-8')
pd.set_option('display.max_colwidth', -1)


def linkfy(name, tp):
    """Return link for comwith ranking."""
    label = name.replace(" ", "_").replace("'", "")
    s = u"<a href=\"{{url_for('rings',time='%s',focus='%s')}}\">%s</a>" % (tp, label, name)
    return s


if __name__ == '__main__':
    # VARIABLES
    IC = "../../InformalCollaboration/Code/"  # relative path of IC repository
    networks = ["auth", "comwith"]
    input_folder = IC + "211_centralities/"
    affiliation_file = IC + "214_node_lists/all-all_all.csv"
    output_folder = "../templates/rankings/"

    timepoints = ['early', 'late']
    measures = ["occurrence", "betweenness", "eigenvector"]

    AFF_LABEL = 'Affiliation (on last published paper)'

    # READ IN
    # DataFrame for affiliations
    aff_df = pd.read_csv(affiliation_file, encoding='utf-8', index_col=0,
                         usecols=['name', 'affiliation'])
    aff_df['affiliation'].fillna(u"", inplace=True)
    aff_df['affiliation'] = aff_df['affiliation'].apply(
        lambda x: x.split('; ')[-1])  # use affiliation of last-published paper
    aff_df.rename(columns={'affiliation': AFF_LABEL},
                  inplace=True)

    # CREATE RANKING
    combs = product(timepoints, networks)
    for (tp, nw) in combs:
        # Read in
        input_file = "{}{}_network/all-{}.csv".format(input_folder, nw, tp)
        rank_df = pd.read_csv(input_file, encoding='utf-8')

        # Merge data
        rank_df = rank_df.merge(aff_df, 'left', left_on='node',
                                right_index=True)
        rank_df[measures] = rank_df[measures].fillna(0)
        rank_df.rename(columns={'node': 'Name'}, inplace=True)

        # Create column with links
        if nw == "comwith":
            rank_df['Name'] = rank_df['Name'].apply(
                lambda x: linkfy(x, tp))

        # Sort and write out
        for measure in measures[:1]:
            rank_meas = measure + '_rank'

            temp = rank_df.sort_values([rank_meas, 'Name'])
            temp.rename(columns={rank_meas: 'Rank', measure: 'Value'},
                        inplace=True)
            temp['Rank'].fillna("-", axis='index', inplace=True)
            temp['Rank'] = temp['Rank'].apply(lambda x: str(x).split('.')[0])

            output_file = '{}all-{}_{}_{}.html'.format(output_folder, nw,
                                                       tp, measure)
            temp[['Rank', 'Name', AFF_LABEL, 'Value']].to_html(
                output_file, index=False, escape=False,
                classes="table table-hover", na_rep="",
                float_format=lambda x: '%10.3f' % x)
