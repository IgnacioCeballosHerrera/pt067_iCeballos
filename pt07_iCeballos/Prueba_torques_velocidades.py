# -*- coding: utf-8 -*-
"""
PRUEBA EFICIENCIAS

@author: Nacho
"""

import numpy as np
import pandas as pd

c = 20
k_w = 10e-5 # perdidas por friccion de viento
k_i = 0.1 # perdidas por hierro (magneticas)
k_c = 0.8 #peridas por cobre (electricas)
 
#%%

def eficiencia(torque, omega):
    '''
    Calcula la eficiencia para un estado de torque y una velodidad angular
    en un motor de modelo magnetico simple con esobillas
    '''
    t = torque
    w = omega
    ef = (t*w) / (t*w + k_w + k_i + k_c + c)
    return ef

v_angulares = np.arange(0,45,5)
torques = np.arange(0,185,5)

#%%
ef_tot = []
for i in range(len(torques)):
    ef_i = []
    for k in range(len(v_angulares)):
        ef_k = eficiencia(torques[i], v_angulares[k])
        ef_i.append(ef_k)
    ef_tot.append(ef_i)
    
eficiencias = pd.DataFrame(ef_tot)
efc = np.array(ef_tot)
        
