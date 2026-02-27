# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # GENESIM with distance weighting
#
# Mariethoz et al. (2010) propose to weight conditional data by distance.
# This is implemented in `mps_genesim` and can be controlled by:
#
#     O.par['distance_measure']  # Distance measure: [1] discrete, [2] continuous
#     O.par['distance_max']      # Maximum distance
#     O.par['distance_pow']      # Power (exponent)
#
# See details about distance weighting in:
# [Mariethoz, Gregoire, Philippe Renard, and Julien Straubhaar. "The direct sampling method to perform multiple-point geostatistical simulations." Water Resources Research 46.11 (2010).](https://doi.org/10.1029/2008WR007621)

# %%
import matplotlib.pyplot as plt
import numpy as np
import mpslib as mps

# %% [markdown]
# ## Setup the MPS object and training image

# %%
O = mps.mpslib(method='mps_genesim',
               verbose_level=-1,
               n_cond=25,
               n_real=1,
               simulation_grid_size=np.array([50, 50, 1]))

O.ti, TI_filename = mps.trainingimages.strebelle(4, coarse3d=0)

# %% [markdown]
# ## Run simulations for varying distance parameters
#
# Loop over combinations of `distance_max` and `distance_pow` and show the resulting realizations.

# %%
distance_max_arr = [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.22, 0.24, 0.26, 0.28, 0.30]
distance_pow_arr = [0, 1, 2]

n1 = len(distance_max_arr)
n2 = len(distance_pow_arr)

T = np.zeros((n1, n2))

fig = plt.figure(figsize=(6, 18))
for i1 in np.arange(n1):
    for i2 in np.arange(n2):

        O.par['distance_max'] = distance_max_arr[i1]
        O.par['distance_pow'] = distance_pow_arr[i2]
        O.par['distance_measure'] = 1  # discrete
        O.run()
        T[i1, i2] = O.time

        print('distance_max=%g distance_pow=%g, t=%4.2fs' % (O.par['distance_max'], O.par['distance_pow'], T[i1, i2]))

        isp = i1 * n2 + i2 + 1
        plt.subplot(n1, n2, isp)
        D = np.squeeze(np.transpose(O.sim[0]))
        plt.imshow(D, interpolation='none', vmin=0, vmax=1)
        plt.title('p=%3.1f, dmax=%3.2f' % (O.par['distance_pow'], O.par['distance_max']))

# %% [markdown]
# ## Computation time vs. distance_max
#
# Plot how computation time varies with `distance_max` for each value of `distance_pow`.

# %%
plt.plot(distance_max_arr, T, '-*')
plt.xlabel('distance_max')
plt.ylabel('Time (s)')
plt.legend(['pow=%d' % p for p in distance_pow_arr])

# %% [markdown]
# ## Inspect final parameter set

# %%
O.par
