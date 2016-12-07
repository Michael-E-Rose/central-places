#!/usr/bin/env python3
"""Generate html for website to display the network rankings."""

from itertools import product

import pandas as pd

pd.set_option('display.max_colwidth', -1)


def linkfy(name, y):
    """Return link for comwith ranking."""
    label = name.replace(" ", "_").replace("'", "")
    s = u"<a href=\"{{url_for('rings',year='%s',focus='%s')}}\">%s</a>" % (y, label, name)
    return s


if __name__ == '__main__':
    # VARIABLES
    networks = ["auth", "com"]
    input_folder = "centralities/"
    output_folder = "../templates/rankings/"

    YEARS = ['2011', '2008', '2005', '2002', '1999']

    # CREATE RANKING
    combs = product(YEARS, networks)
    for (y, nw) in combs:
        if nw == "auth":
            measures = ["papers", "betweenness", "eigenvector"]
        else:
            measures = ["thanks", "betweenness", "eigenvector"]

        # Read in
        input_file = "{}{}_{}.csv".format(input_folder, nw, y)
        df = pd.read_csv(input_file, encoding='utf-8')

        df[measures] = df[measures].fillna(0)
        df.rename(columns={'node': 'Name'}, inplace=True)

        # Create column with links
        if nw == "com":
            df['Name'] = df['Name'].apply(lambda x: linkfy(x, y))

        # Sort and write out
        for measure in measures:
            rank_meas = measure + '_rank'

            temp = df.sort_values([rank_meas, 'Name'])
            temp = temp.rename(columns={rank_meas: 'Rank', measure: 'Value'})
            temp['Rank'] = temp['Rank'].fillna("-").astype(str)
            temp['Rank'] = temp['Rank'].apply(lambda x: x.split('.')[0])
            if measure in ('thanks', 'papers'):
                temp['Value'] = temp['Value'].astype(int)
            output_file = '{}{}_{}_{}.html'.format(output_folder, nw,
                                                   y, measure)
            temp[['Rank', 'Name', 'Value']].to_html(
                output_file, index=False, escape=False,
                classes="table table-hover", na_rep="",
                float_format=lambda x: '%10.3f' % x)
