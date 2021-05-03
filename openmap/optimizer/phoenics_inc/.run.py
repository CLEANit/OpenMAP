#!/usr/bin/env python

__author__ = 'Florian Hase'

#========================================================================

import warnings
warnings.filterwarnings('ignore')

import pickle
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns

colors = sns.color_palette('RdYlBu', 8)
colors = [colors[-1], colors[0]]

from gryffin import Phoenics

#========================================================================

max_iter = 10**8

#========================================================================

def loss(vector):
	loss_value = (0.5 * (vector[0] + 1.))**2 + (0.1 * (vector[1] - 0.))**2
	return loss_value

def evaluate(samples):
	vector = np.array([samples['param_0'], samples['param_1']])
	vector = np.squeeze(vector)
	obs    = loss(vector)
	obs_dict = {key: samples[key] for key in samples}
	obs_dict['obj_0'] = obs
	return obs_dict

#========================================================================


config_file = 'config.json'
phoenics    = Phoenics(config_file)

fig = plt.figure(figsize = (6, 6))
ax0 = plt.subplot2grid((2, 2), (0, 0))
ax1 = plt.subplot2grid((2, 2), (1, 0))
ax2 = plt.subplot2grid((2, 2), (1, 1))
axs = [ax0, ax1, ax2]

plt.ion()

observations = []
for _ in range(max_iter):

#	if _ == 2: 
#		quit()

	samples = phoenics.recommend(observations = observations)

	new_observations = []
	for sample in samples:
		new_obs = evaluate(sample)
		new_observations.append(new_obs)
	
	observations.extend(new_observations)

	with open('observations.pkl', 'wb') as content:
		pickle.dump(observations, content)

	continue

	for ax in axs:
		ax.cla()

	# plotting ground truth
	x_domain = np.linspace(-2., 0., 100)
	y_domain = np.linspace(-5., 5., 100)
	X, Y = np.meshgrid(x_domain, y_domain)
	Z    = np.zeros((len(x_domain), len(y_domain)))
	for x_index, x_element in enumerate(x_domain):
		for y_index, y_element in enumerate(y_domain):
			loss_value = loss([x_element, y_element])
			Z[y_index, x_index] = loss_value

	levels = np.linspace(np.amin(Z), np.amax(Z), 256)
	ax0.contourf(X, Y, Z, cmap = plt.cm.bone_r, levels = levels)

	# plotting surrogates	
	kernel              = phoenics.bayesian_network.kernel_contribution
	sampling_parameters = phoenics.bayesian_network.sampling_param_values

	Z    = np.zeros((len(x_domain), len(y_domain)))
	for x_index, x_element in enumerate(x_domain):
		for y_index, y_element in enumerate(y_domain):
			param = np.array([x_element, y_element, 0., 0., 0.])   #, dtype = np.float32)
			num, den = kernel(param)
			loss_value = (num + sampling_parameters[0]) * den
			Z[y_index, x_index] = loss_value

	levels = np.linspace(np.amin(Z), np.amax(Z), 256)
	ax1.contourf(X, Y, Z, cmap = plt.cm.bone_r, levels = levels)

	print('SAMPLING_PARAMETERS', sampling_parameters)

	# plotting surrogates	
	Z    = np.zeros((len(x_domain), len(y_domain)))
	for x_index, x_element in enumerate(x_domain):
		for y_index, y_element in enumerate(y_domain):
			param = np.array([x_element, y_element, 0., 0., 0.])   #, dtype = np.float32)
			num, den = kernel(param)
			loss_value = (num + sampling_parameters[1]) * den
			Z[y_index, x_index] = loss_value

	levels = np.linspace(np.amin(Z), np.amax(Z), 256)
	ax2.contourf(X, Y, Z, cmap = plt.cm.bone_r, levels = levels)


	for obs_index, obs in enumerate(observations):
		ax0.plot(obs['param_0'], obs['param_1'], marker = 'o', color = colors[obs_index % len(colors)], markersize = 5)
		ax1.plot(obs['param_0'], obs['param_1'], marker = 'o', color = colors[obs_index % len(colors)], markersize = 5)
		ax2.plot(obs['param_0'], obs['param_1'], marker = 'o', color = colors[obs_index % len(colors)], markersize = 5)
	
	for obs_index, obs in enumerate(new_observations):
		ax0.plot(obs['param_0'], obs['param_1'], marker = 'D', color = colors[obs_index % len(colors)], markersize = 8)
		ax1.plot(obs['param_0'], obs['param_1'], marker = 'D', color = colors[obs_index % len(colors)], markersize = 8)
		ax2.plot(obs['param_0'], obs['param_1'], marker = 'D', color = colors[obs_index % len(colors)], markersize = 8)

	plt.pause(0.05)
	observations.extend(new_observations)
