#!/usr/bin/env python2.7
"""Source code for website."""

from flask import abort, Flask, render_template, request
from flask_bootstrap import Bootstrap


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


@app.route('/bibliography')
def bibliography():
    return render_template('bibliography.html')


@app.route('/rankings')
def rankings():
    rtypes = ['com', 'auth']
    years = ['2011', '2008', '2005', '2002', '1999']
    rankings = ['thanks', 'papers', 'betweenness', 'eigenvector']
    rtype = request.args.get('rtype', default='com')
    year = request.args.get('year', default='2011')
    ranking = request.args.get('ranking', default='thanks')
    if rtype in rtypes and year in years and ranking in rankings:
        return render_template('rankings.html', rtype=rtype, year=year,
                               ranking=ranking, this_site='rankings')
    else:
        return abort(404)


@app.route('/networks')
def networks():
    year = request.args.get('year', default='2011')
    years = ['2011', '2008', '2005', '2002', '1999']
    if year in years:
        return render_template('networks.html', year=year,
                               this_site='networks')
    else:
        return abort(404)


@app.route('/rings')
def rings():
    focus = request.args.get('focus', default="RENE_M_STULZ").replace("_", " ")
    year = request.args.get('year', default='2011')
    years = ['2011', '2008', '2005', '2002', '1999']
    if year in years:
        return render_template('rings.html', focus=focus, year=year,
                               this_site='rings')
    else:
        return abort(404)


@app.route('/about')
def about():
    return render_template('about.html', this_site='about')


# Launch for Testing
if __name__ == '__main__':
    app.run(port=8000)
