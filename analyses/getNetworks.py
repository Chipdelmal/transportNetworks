#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import osmnx as ox
import setup as stp
import style as sty
import pandas as pd
import pickle as pkl
import networkx as nx
import functions as fun
import matplotlib.pyplot as plt

###############################################################################
# Setup and check OSMNX
###############################################################################
ox.config(log_console=True, use_cache=True)
print('OSMNXv{}'.format(ox.__version__))

n = 30
(PLACE, netType, EXPORT, FMT, PTH_BASE) = (
        'San Francisco, California, USA', 'drive', True,
        stp.FMT, stp.PTH_BASE
    )
idStr = '-'.join([i[:].replace(' ', '') for i in PLACE.split(',')])
###############################################################################
# Get Network and Projections
###############################################################################
G = ox.graph_from_place(PLACE, netType)
G = ox.project_graph(G)
gdf = ox.gdf_from_place(PLACE)
area = ox.project_gdf(gdf).unary_union.area
if EXPORT:
    file = open('{}/dta/{}-{}-G.pickle'.format(PTH_BASE, idStr, netType), 'wb')
    pkl.dump(G, file)
    file.close()

###############################################################################
# Plot the original network
###############################################################################
(fig, ax) = ox.plot_graph(
        G, show=False,
        bgcolor=sty.BKG,
        node_size=sty.NS*2, node_color=sty.NC, node_zorder=sty.NZ,
        edge_linewidth=sty.ES, edge_color=sty.EC, edge_alpha=sty.EA
    )
if EXPORT:
    fig.savefig(
            '{}/img/{}-{}-O.{}'.format(PTH_BASE, idStr, netType, FMT),
            bbox_inches='tight', pad_inches=.01
        )

###############################################################################
# Bearings
###############################################################################
G = ox.add_edge_bearings(G)
bearings = pd.Series([
        data['bearing'] for u, v, k, data in G.edges(keys=True, data=True)
    ])


(count, division) = np.histogram(
        bearings,
        bins=[ang*360/n for ang in range(0,n+1)]
    )
(division, width) = (division[0:-1], 2 * np.pi / n)
(fig, ax) = plt.subplots()
ax = plt.subplot(111, projection='polar')
ax.set_theta_zero_location('N')
ax.set_theta_direction('clockwise')
bars = ax.bar(
        division * np.pi/180 - width * 0.5, count,
        width=width, bottom=0.0
    )
if EXPORT:
    fig.savefig(
            '{}/img/{}-{}-D.{}'.format(PTH_BASE, idStr, netType, FMT),
            bbox_inches='tight', pad_inches=.01
        )

###############################################################################
# Network stats
###############################################################################
stats = ox.basic_stats(G, area=area)
extended_stats = ox.extended_stats(G, ecc=True, bc=True, cc=True)
for key, value in extended_stats.items():
    stats[key] = value

if EXPORT:
    statSeries = pd.Series(stats)
    statSeries.to_csv('{}/dta/{}-{}-S.csv'.format(PTH_BASE, idStr, netType))
    file = open('{}/dta/{}-{}-S.pickle'.format(PTH_BASE, idStr, netType), 'wb')
    pkl.dump(stats, file)
    file.close()

###############################################################################
# Betwenness Centrality
###############################################################################
nc = fun.get_node_colors_by_stat(
        G, data=extended_stats['betweenness_centrality']
    )
(fig, ax) = ox.plot_graph(
        G, show=False,
        bgcolor=sty.BKG,
        node_size=sty.NS*2, node_color=nc, node_zorder=sty.NZ,
        edge_linewidth=sty.ES/2, edge_color=sty.EC, edge_alpha=sty.EA
    )
if EXPORT:
    fig.savefig(
            '{}/img/{}-{}-B.{}'.format(PTH_BASE, idStr, netType, FMT),
            bbox_inches='tight', pad_inches=.01
        )
