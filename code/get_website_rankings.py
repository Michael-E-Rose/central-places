#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Generates html for website to display the network rankings."""

from glob import glob
from os.path import basename, splitext

import pandas as pd

SOURCE_FOLDER = "centralities/"
TARGET_FOLDER = "../templates/rankings/"

pd.set_option('display.max_colwidth', -1)


def linkfy(name, y):
    """Return link for ring view."""
    label = name.replace(" ", "_").replace("'", "")
    s = u"<a href=\"{{url_for('rings',year='%s',focus='%s')}}\">%s</a>" % (y, label, name)
    return s


def main():
    for file in glob(SOURCE_FOLDER + "*.csv"):
        nw, year = splitext(basename(file))[0].split("_")
        if nw == "auth":
            measures = ["papers", "betweenness", "eigenvector"]
        elif nw == "com":
            measures = ["thanks", "betweenness", "eigenvector"]
        else:
            measures = ["thanks", "papers", "betweenness", "eigenvector"]

        # Read in
        df = pd.read_csv(file).rename(columns={'node': 'Name'})

        # Create column with links
        if nw == "both":
            df['Name'] = df['Name'].apply(lambda x: linkfy(x, year))

        # Sort and write out
        for measure in measures:
            rank_meas = measure + '_rank'
            temp = (df.dropna(subset=[measure])
                      .sort_values([rank_meas, 'Name'])
                      .rename(columns={rank_meas: 'Rank', measure: 'Value'}))
            temp['Rank'] = (temp['Rank'].fillna("-").astype(str)
                                        .apply(lambda x: x.split('.')[0]))
            if measure in ('thanks', 'papers'):
                temp['Value'] = temp['Value'].astype(int)
            output_file = '{}{}_{}_{}.html'.format(TARGET_FOLDER, nw,
                                                   year, measure)
            temp[['Rank', 'Name', 'Value']].to_html(
                output_file, index=False, escape=False,
                classes="table table-hover", na_rep="",
                float_format=lambda x: '%10.3f' % x)


if __name__ == '__main__':
    main()
