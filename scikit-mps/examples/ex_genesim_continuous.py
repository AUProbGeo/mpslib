#!/usr/bin/env python
# coding: utf-8

# # GENESIM with continuous training image
# 
# Mariethoz et al. (2010) propose to weight conditonal data by distance. This is implemented with mps_genesim, and can be controlled by
# 
#     O.par['distance_measure'] # Distance measure [1]: discrete, [2]: continous
#     O.par['distance_min'] ; # Max distance
#     O.par['distance_pow'] ; # Power
# 
# See details about distance weighing in [Mariethoz, Gregoire, Philippe Renard, and Julien Straubhaar. "The direct sampling method to perform multiple‐point geostatistical simulations." Water Resources Research 46.11 (2010).
# ](https://doi.org/10.1029/2008WR007621).

# In[1]:


# import mpslib as mps
import matplotlib.pyplot as plt
import numpy as np
import mpslib as mps


# In[ ]:





# In[2]:


O=mps.mpslib(method='mps_genesim', 
             verbose_level=0, 
             n_cond = 25,
             n_real=4, 
             simulation_grid_size=np.array([50, 50, 1]));

O.ti, TI_filename = mps.trainingimages.stones()
O.delete_local_files()
plt.imshow(O.ti[:,:,0].T, interpolation='none', vmin=0, vmax=256, cmap='gray')


# In[3]:


O.par['distance_max']=25
O.par['distance_pow']=2
O.par['distance_measure']=2 # continuous
O.run_parallel()


# In[4]:


O.plot_reals(cmap='gray')


# In[5]:


distance_max_arr = [40,39,38,37,36,35,34,33,32,31,30,25,20,10]
distance_pow_arr = [0, 1, 2]

n1=len(distance_max_arr)
n2=len(distance_pow_arr)

T=np.zeros((n1,n2))

fig = plt.figure(figsize=(6, 12))
for i1 in np.arange(n1):
    for i2 in np.arange(n2):
        
        O.par['distance_max']=distance_max_arr[i1]
        O.par['distance_pow']=distance_pow_arr[i2]
        O.par['distance_measure']=2 # continuous
        O.run()
        T[i1,i2]=O.time
        
        print('distance_max=%g distance_pow=%g, t=%4.2fs' % (O.par['distance_max'],O.par['distance_pow'],T[i1,i2]))
        
        
        isp = i1*n2+i2+1    
        plt.subplot(n1,n2,isp)
        D=np.squeeze(np.transpose(O.sim[0]));
        plt.imshow(D, interpolation='none', vmin=0, vmax=256, cmap='gray')
        plt.title('p=%3.1f, dmax=%3.2f' % (O.par['distance_pow'],O.par['distance_max']) )
            


# In[6]:


plt.semilogy(distance_max_arr,T,'-*')
plt.xlabel('distance_max')
plt.ylabel('Time (s)')
#plt.legend()


# In[ ]:





# In[ ]:




