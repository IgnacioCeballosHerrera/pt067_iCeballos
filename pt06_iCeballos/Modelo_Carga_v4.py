# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 11:23:48 2023

@author: Nacho
"""

import numpy as np
import pandas as pd
from datetime import time, date
import matplotlib.pyplot as plt
import glob

def demanda_en_dia(demanda_auto):
    '''
    Toma un dataframe que contiene la potencia consumida en ciertos minutos del dia por un vehiculo
    y genera un vector de numpy con esta misma demanda inserta en el dia completo
    '''
    potencia = np.array(demanda_auto['Potencia [kW]'])
    minutos = np.array(demanda_auto['tiempo [min]'])
    
    base = np.arange(60*24)
    k = 0 #contador
    
    for i in range(len(base)):
        if k == len(potencia):
            break
        if base[i] == minutos[k]:
            base[i] = potencia[k]
            k = k+1
        else:
            base[i] = 0
    
    return base

def extraer_csvs(nombre_carpeta):
    '''
    Lee todos los csvs dentro de una carpeta y luego crea una lista con
    Dataframes de panda, donde cada uno tiene el contenido de un csv
    
    nombre_carpeta (str): Directorio y nombre de carpeta que se quiere leer 
    
    main_list (list(DataFrames)): Lista que contiene dataframes con la info
    extraida de cada csv dentro de la carpeta

    '''
    # Utiliza glob para obtener la lista de todos los archivos CSV en la carpeta.
    folder_path = nombre_carpeta
    file_list = glob.glob(folder_path + "/*.csv")

    # Lee el primer archivo CSV en la lista y crea un DataFrame principal llamado main_dataframe.
    main_dataframe = pd.DataFrame(pd.read_csv(file_list[0]))
    main_list = [main_dataframe]

    # Itera sobre los archivos restantes en la lista.
    for i in range(1, len(file_list)):
        # Lee cada archivo CSV y crea un DataFrame llamado df.
        data = pd.read_csv(file_list[i])
        df = pd.DataFrame(data)
        main_list.append(df)
        # Concatena el DataFrame actual (df) al DataFrame principal (main_dataframe) a lo largo del eje 1 (columnas).
        # main_dataframe = pd.concat([main_dataframe, df], axis=1)
    return main_list

def buscar_cargador(Rapidos): # def buscar_cargador(Rapidos, Lentos):
    '''
    Busca un cargador para el vehiculo que solicita carga, devolviendo si hay cargador
    disponible con busqueda=1, y en c_rapido o c_lento el indice del cargador asignado
    Si busqueda=0 se seguira con otro algoritmo para otorgar un lugar en la fila
    '''
    busqueda = 0
    c_rapido = 0
    #c_lento = 0
    
    for i in range(len(Rapidos)):
        if Rapidos.iloc[i]['Estado'] == 0:
            busqueda = 1
            c_rapido = i
            Rapidos.iloc[i]['Estado'] = 1
            break
    
    return busqueda, c_rapido #, c_lento

def crear_cargadores(n_rapidos, n_lentos, p_rapidos, p_lentos):
    '''
    Crea diccionarios con cargadores rapidos y lentos, que incluyen informacion 
    de carga maxima y estado de uso (binario)
    '''
    rapidos = pd.DataFrame([], columns=['Estado','Potencia maxima'])
    for j in range(n_rapidos):
        nombre_j = 'Rapido '+ str(j)
        rapidos.loc[nombre_j] = [0, p_rapidos]
    
    lentos = pd.DataFrame([], columns=['Estado','Potencia maxima'])
    for i in range(n_lentos):
        nombre_i = 'Lento '+ str(i)
        lentos.loc[nombre_i] = [0, p_lentos]
        
    return rapidos, lentos

def demanda_a_minutos(demanda_en_horas):
    '''
    Toma una demanda diaria en horas y la trnasforma en una demanda diaria pero en minutos
    '''
    n_minutos = np.ones(60*24)
    for i in range(len(n_minutos)):
        contador = int(i/60)
        n_minutos[i] = n_hora[contador]
    
    return n_minutos

# Define la ruta de la carpeta que contiene archivos CSV con los tipos de autos
directorio_carpeta = 'Datos_entrada/Demanda_carga'
df_autos = extraer_csvs(directorio_carpeta)

# Importar demanda de carga
# Por ahora se esta suponiendo que el cargador es capaz de cargar a la potencia solicitada,

demanda_0 = pd.read_csv('Datos_entrada/Demanda_carga/prueba.csv')

# Crea una columna de tiempo en segundos y aproxima sus valores a enteros
demanda_0['tiempo [min]'] = demanda_0['tiempo [h]']*60
for j in range(len(demanda_0['tiempo [min]'])):
    demanda_0['tiempo [min]'].iloc[j] = int(demanda_0['tiempo [min]'].iloc[j])


#autos que cargan por hora y por minuto
n_hora = np.array([1,1,1,1,1,1,2,2, 2,3,4,4,4,5,5,5, 4,4,4,3,3,2,2,2])
n_minutos = demanda_a_minutos(n_hora) 
    
    
#%%


# Info cargadores
n_rapidos = 8 # Sobre 22 kW
n_lentos = 3 # Bajo 22 kW

p_max_rapido = 150
p_max_lento = 22

# Creacion de cargadores lentos y rapidos con potencias maximas y estado desocupado por defecto
Rapidos, Lentos = crear_cargadores(n_rapidos,n_lentos, p_max_rapido, p_max_lento)


lista_espera = [] # Podria contener info de carga del tipo [pot_carga_j, carga_solicitada_j (J), tiempo_carga_j]
demanda = []

# j para vehiculos, i para horas del dia
for i in range(len(n_hora)):
    auto = 1
    minutos = i*60 # cantidad de minutos que han pasado respecto al comienzo del dia
    if n_hora[i] != 0: # Evalua si la demanda es nula, sino debe ponerse a la lista
        # Anade cada demanda al vector lista de espera
        for j in range(n_hora[i]):
        # Esto deberia ser una distribucion para elegir vehiculos y sus caracteristicas
            demanda_auto_j = demanda_0[['Potencia [kW]', 'tiempo [min]']].copy() #demanda_0[['Potencia [kW]', 'tiempo [min]', 'soc [%]']].copy()
            lista_espera.append(demanda_auto_j)
           
    while len(lista_espera) > 0:
        turno_j = lista_espera[0]
        t_total_carga = demanda_0['tiempo [min]'].iloc[-1] # en minutos
        match, cargador_j = buscar_cargador(Rapidos)
        
        if match == 1: # es decir, si encontro cargador
            demanda_j = turno_j # de la forma [p_carga_j, t_carga_j, soc_carga_j]
            turno_j['tiempo [min]'] = turno_j['tiempo [min]'] + minutos
            demanda.append(demanda_j)
            # demanda.sort_values(by = 'tiempo [min]')
            # break
            del lista_espera[0]
        else:
            break # por ahora solo pasa a la hora siguiente si no hay cargadores
        # crear algoritmo de desocupado ###!!!


# Inserta la demanda de cada auto en un vector dia (en minutos)
demandas_por_auto = []
for j in demanda:
    demandas_por_auto.append(demanda_en_dia(j))
demanda_diaria = abs(sum(demandas_por_auto))

plt.figure()
plt.plot(demanda_diaria)
plt.ylabel('Potencia [kW]')
plt.xlabel('Tiempo [min]')
# for j in demandas_por_auto:
#     plt.plot(j)
plt.grid()
plt.show
    