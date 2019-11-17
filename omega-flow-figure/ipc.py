#!/usr/bin/env python3

import os.path as osp
import sys

sys.path.append('.')

import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import common as c
import target_stats as t

show_lins = 62
pd.set_option('precision', 3)
pd.set_option('display.max_rows', show_lins)
pd.set_option('display.min_rows', show_lins)

full = False
if full:
    suffix = '-full'
else:
    suffix = ''
stat_dirs = {
        # 'Xbar4': 'xbar4',
        'Xbar4': 'xbar4-rand',
        # 'Xbar4-SpecSB': 'xbar4-rand-hint',
        # 'Xbar4*2-SpecSB': 'dedi-xbar4-rand-hint',
        #'Omega16': 'omega',
        #'Omega16-OPR': 'omega-rand',
        'Omega16-OPR-SpecSB': 'omega-rand-hint',
        #'Xbar16': 'xbar',
        #'Xbar16-OPR': 'xbar-rand',
        #'Xbar16-OPR-SpecSB': 'xbar-rand-hint',
        'Ideal-OOO': 'ruu-4-issue',
        }
for k in stat_dirs:
    stat_dirs[k] = c.env.data(f'{stat_dirs[k]}{suffix}')

configs_ordered = ['Xbar4', 'Omega16-OPR-SpecSB', 'Ideal-OOO']

colors = ["r","gray"]

benchmarks = [*c.get_spec2017_int(), *c.get_spec2017_fp()]

points = []
for b in benchmarks:
    for i in range(0, 3):
        points.append(f'{b}_{i}')

fig, ax = plt.subplots()
fig.set_size_inches(14, 4, forward=True)
width = 0.6
interval = 0.4

rects = []

num_points = 0
num_configs = len(stat_dirs)
dfs = dict()
for config in configs_ordered:
    print(config)
    stat_dir = stat_dirs[config]
    stat_dir = osp.expanduser(stat_dir)
    stat_files = [osp.join(stat_dir, point, 'stats.txt') for point in points]

    matrix = {}
    for point, stat_file in zip(points, stat_files):
        d = c.get_stats(stat_file, t.ipc_target, re_targets=True)
        matrix[point] = d

    df = pd.DataFrame.from_dict(matrix, orient='index')

    dfs[config] = df

    if num_points == 0:
        num_points = len(df)

dfs['Ideal-OOO'].loc['rel_geo_mean'] = [1.0]
print('Ideal-OOO')
print(dfs['Ideal-OOO'])
for config in configs_ordered:
    if config != 'Ideal-OOO':
        print(config)
        rel = dfs[config]['ipc'] / dfs['Ideal-OOO']['ipc'][:-1]
        dfs[config]['rel'] = rel

        dfs[config].loc['rel_geo_mean'] = [rel.prod() ** (1/len(rel))] * 2

        if config == 'Omega16-OPR-SpecSB':
            dfs[config]['boost'] = dfs[config]['rel'] / dfs['Xbar4']['rel']

        print(dfs[config])
num_points += 1

do_normalization = True
data_all = []
for i, config in enumerate(configs_ordered):
    df = dfs[config]
    # whitespace before geomean
    data = np.concatenate((df['ipc'].values[:-1], np.ones(1) if i == 2 else np.zeros(1), df['ipc'].values[-1:]))
    data_all.append(data)
num_points += 1
data_all = np.array(data_all)

if do_normalization:
    data_all = np.array([data_all[0] / data_all[2], data_all[1] / data_all[2]])
    print(data_all, data_all.shape)
    num_configs -= 1

print(num_points, num_configs)
shift = 0.0
for i, data in enumerate(data_all):
    tick_starts = np.arange(0, num_points * num_configs, (width + interval) * num_configs) + shift

    # print(tick_starts)
    rect = plt.bar(tick_starts, data,
        edgecolor='black',
        color=colors[i], width=width)
    rects.append(rect)
    shift += width + interval

benchmarks_ordered = []
for point in df.index:
    if point.endswith('_0'):
        benchmarks_ordered.append(point.split('_')[0])

ax.xaxis.set_major_locator(mpl.ticker.IndexLocator(base=(width+interval)*num_configs*3, offset=-interval/2))
ax.xaxis.set_minor_locator(mpl.ticker.IndexLocator(base=(width+interval)*num_configs, offset=-interval/2))

ax.xaxis.set_major_formatter(mpl.ticker.NullFormatter())
# ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())

ax.set_xlim(left=-0.5, right=num_points * num_configs)
ax.set_ylim((0, 1.13 if do_normalization else 3))

for tick in ax.xaxis.get_major_ticks():
    tick.tick1line.set_markersize(10)
    tick.tick2line.set_markersize(0)

for tick in ax.xaxis.get_minor_ticks():
    tick.tick1line.set_markersize(2)
    # tick.tick2line.set_markersize(0)
    tick.label1.set_horizontalalignment('left')

xticklabels = [''] * num_points
print(len(xticklabels))
for i, benchmark in enumerate(benchmarks_ordered + ['rel_geomean']):
    xticklabels[i*2] = benchmark
ax.set_xticklabels(xticklabels, minor=True, rotation=90)

ax.grid(axis="y", linestyle="--", color='gray')
ax.set_ylabel('Normalized IPCs')
ax.set_xlabel('Simulation points from SPEC 2017')
ax.legend(rects, configs_ordered, fontsize='small', ncol=num_configs, 
        loc='lower left', bbox_to_anchor=(0.788,0.88))


plt.tight_layout()
for f in ['eps', 'png']:
    plt.savefig(f'./{f}/ipc.{f}', format=f'{f}')

plt.show()
