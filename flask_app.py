#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Generates websites."""

from flask import abort, Flask, render_template, request
from flask_bootstrap import Bootstrap

_years = [str(y) for y in range(1999, 2011+1)]


# Intitialization
app = Flask(__name__)
app.config.from_object(__name__)
app.url_map.strict_slashes = False
bootstrap = Bootstrap(app)


# Controllers
@app.route('/', defaults={'this_site': 'index'})
@app.route('/index', defaults={'this_site': 'index'})
def index(this_site):
    return render_template('index.html', this_site='index')


@app.route('/rankings')
def rankings():
    rankings = ['thanks', 'papers', 'betweenness', 'eigenvector']
    year = request.args.get('year', default='2011')
    ranking = request.args.get('ranking', default='thanks')
    if year in _years and ranking in rankings:
        return render_template('rankings.html', year=year, ranking=ranking,
                               this_site='rankings')
    else:
        return abort(404)


@app.route('/rings')
def rings():
    focus = request.args.get('focus', default="Spiegel,_Matthew").replace("_", " ")
    year = request.args.get('year', default='2011')
    if year in _years:
        return render_template('rings.html', focus=focus, year=year,
                               this_site='rings')
    else:
        return abort(404)



# Launch for Testing
if __name__ == '__main__':
    app.run(port=7000)
