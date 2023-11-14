# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 11:23:48 2023

@author: Nacho
"""

import numpy as np

#autos que cargan por hora
n_hora = np.array([1,1,1,1,1,1,2,2,\
                       2,3,4,4,4,5,5,5,\
                           4,4,4,3,3,2,2,2])
#potencia requerida por cada vehiculo kW
dist_carga = np.array([22.4,44.6])

#capacidad de banco de baterias de vehiculo kWh
# capacidad = np.array([40, 60, 80])
capacidad = np.array([20, 40, 60]) # por ahora corresponde a lo que van a cargar, no al total de lo que pueden cargar

#cargadores disponibles
cargadores_rapidos = 6 # Sobre 22 kW
n_lentos = 3 # Bajo 22 kW

demanda_hora = []
for i in n_hora:
    demanda_i = []
    for j in range(i):
        pot_carga = np.random.choice(dist_carga)
        cap_carga = np.random.choice(capacidad)
        horas_carga_j =  capacidad/pot_carga
        

        
    
    
    
    









