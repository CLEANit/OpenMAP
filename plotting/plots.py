#!/usr/bin/env python

import os, sys
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import glob

#===============================================================================

# directory which stores the runs
dir = '../runs'

# choose from traces, percent_space
kind = sys.argv[1]
#kind = 'percent_eval'
#===============================================================================

box_plot = {'x': [], 'kind': [], 'bulk_modulus': []}

if kind == 'traces':
    filenames = glob.glob(f'{dir}/rand_*')
    all_results = []
    for file in filenames:
        results = pickle.load(open(file, 'rb'))
        #all_results.append(results)
        exp = {'eval': [], 'bulk_modulus': [], 'max_bulk_modulus': []} #results['observations_exp']
        for _, obs in enumerate(results):
            exp['eval'].append(_+1)
            exp['bulk_modulus'].append(obs['bulk_modulus'])
            box_plot['bulk_modulus'].append(obs['bulk_modulus'])
            box_plot['kind'].append('random')
            box_plot['x'].append('binding energies')
            if _ == 0:
                max = obs['bulk_modulus']
                exp['max_bulk_modulus'].append(max)
            else:
                if obs['bulk_modulus'] > max:
                    max = obs['bulk_modulus']
                exp['max_bulk_modulus'].append(max)
        all_results.append(exp)

    dfs = [pd.DataFrame(res) for res in all_results]
    df_rand  = pd.concat(dfs)

    filenames = glob.glob(f'{dir}/gryf_*')
    all_results = []
    for file in filenames:
        results = pickle.load(open(file, 'rb'))
        #all_results.append(results)
        exp = {'eval': [], 'bulk_modulus': [], 'max_bulk_modulus': []} #results['observations_exp']
        for _, obs in enumerate(results):
            exp['eval'].append(_+1)
            exp['bulk_modulus'].append(obs['bulk_modulus'])
            box_plot['bulk_modulus'].append(obs['bulk_modulus'])
            box_plot['kind'].append('naive Gryffin')
            box_plot['x'].append('binding energies')
            if _ == 0:
                max = obs['bulk_modulus']
                exp['max_bulk_modulus'].append(max)
            else:
                if obs['bulk_modulus'] > max:
                    max = obs['bulk_modulus']
                exp['max_bulk_modulus'].append(max)
        all_results.append(exp)

    dfs = [pd.DataFrame(res) for res in all_results]
    df_gryf  = pd.concat(dfs)


    fig = plt.figure(figsize = (8, 8))
    sns.lineplot(x = 'eval', y = 'max_bulk_modulus', data = df_rand, label = 'random sampling', linewidth=4)
    sns.lineplot(x = 'eval', y = 'max_bulk_modulus', data = df_gryf, label = 'naive Gryffin',   linewidth=4)

    plt.xlabel('# evaluations', fontsize = 15)
    plt.ylabel('maximum bulk_modulus value found [au]', fontsize = 15)
    #plt.hlines(41.0518, 1, 10, ls = '--', linewidth=2, alpha = 0.5, label = 'global maximum')
    plt.legend(fontsize = 12,  loc='lower right')
    plt.show()
    plt.savefig('traces.png')
#===============================================================================

if kind == 'percent_eval':

    results = {'x': [], 'kind': [], 'percent_eval': []}

    filenames = glob.glob(f'{dir}/rand_*')
    for file in filenames:
        res = pickle.load(open(file, 'rb'))
        obj = np.array([m['obj'] for m in res])
        arg = np.argmin(obj)
        percent_eval = 100*(arg/len(obj))
        results['x'].append('x')
        results['kind'].append('rand')
        results['percent_eval'].append(percent_eval)

    filenames = glob.glob(f'{dir}/gryf_*')
    for file in filenames:
        res = pickle.load(open(file, 'rb'))
        obj = np.array([m['obj'] for m in res])
        arg = np.argmin(obj)
        percent_eval = 100*(arg/len(obj))
        results['x'].append('x')
        results['kind'].append('gryf_naive')
        results['percent_eval'].append(percent_eval)

    filenames = glob.glob(f'{dir}/gryf_static*')
    for file in filenames:
        res = pickle.load(open(file, 'rb'))
        obj = np.array([m['obj'] for m in res])
        arg = np.argmin(obj)
        percent_eval = 100*(arg/len(obj))
        results['x'].append('x')
        results['kind'].append('gryf_static')
        results['percent_eval'].append(percent_eval)

    fig = plt.figure(figsize = (8, 8))
    df = pd.DataFrame(results)
    #sns.violinplot(x = 'x', y = 'percent_eval', hue = 'kind', data = df)
    sns.swarmplot(x = 'x', y = 'percent_eval', hue = 'kind', data = df)
    sns.boxplot(x = 'x', y = 'percent_eval', hue = 'kind', data = df)
    plt.legend()
    plt.show()
    plt.savefig('violin.png')
