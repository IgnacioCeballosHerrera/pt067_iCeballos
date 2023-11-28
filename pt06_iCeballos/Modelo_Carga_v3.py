# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 11:23:48 2023

@author: Nacho
"""

import numpy as np
import pandas as pd
from datetime import time
from datetime import date

''' 
Idea de codigo:
    La idea es que cada auto tenga una funcion demanda dada por steps, que cubriran algun rango horario.
    De esta forma el primer vehiculo llegara a demandar carga a una hora n entre 0 y 24 (por ahora llega justo a esa hora)
    su demanda comenzara en n, y dependiendo del modelo de carga de Esteban, se tomara un tiempo de carga dado por la funcion
    de los steps que usan fracciones de hora como medida (en realidad son fracciones del tiempo final de carga, creo).
    
    Luego debe existir un contador de cargadores totales para decir si es posible que se enchufe otro auto o deba pasar a la fila.
    Otra forma de hacerlo seria tener un indicador binario por cada auto para determinar si se puede cargar ahi o no, y que cuando
    se desocupe el cargador, podamos tener una nueva carga en ese con el vehiculo en la fila de espera. Para esto que es mas complejo
    y completo, sería buenno tener un indicador también para decir el numero en la fila de espera del cargador.
    
    Decidir por parte de cada auto la probabilidad de que este auto cargue en determinado punto de carga (debido a que puede ser carga
    lenta o rapida) puede ser una funcion de probabilidad.
    
Pseudocodigo:
    Tener un for para cada hora de demanda, donde se ingresa un array con las demandas de carga por hora (h)
    
    Cada vehiculo (v) tiene una demanda de carga asociada, y una capacidad maxima de potencia a la que puede carga
    Estas pueden ser por ahora, obtenidas de manera random de un vector con distintos valores para cada una
    Podría simplificarse para que fuese un valor fijo de cada una por ahora
    
    Se evalua si hay cargadores disponibles, buscando siempre el cargador disponible de mayor potencia de carga, pero que no supere
    la potencia maxima del vehiculo
    
        Si hay alguno, este vehiculo carga en ese cagador, el indice binario de estado de ocupado/desocupado cambia a ocupado
        hasta el tiempo final de carga
        Se crea una funcion de valor step(t) que parte en la hora que demanda. Esta demanda se añade a una lista de demandas
        De esta forma se tiene claro cuantos autos cargaron, y para tener la demanda horaria solo hay que sumarlas.
        
        Si no hay alguno, se le asigna un valor en la fila de espera. Este fila de espera permite que el sujeto se conecte
        x minutos despues (tiempo que sale el auto y entra el siguiente) de que desocupo un cargador.
        Se ignoran por ahora los modelos de decision en donde, por ejemplo, se desocupara un carga rapida en 5 minutos mas.
        
    Es necesario dejar pasar a al fila de espera antes que a los otros autos, por lo que debe haber un if fila de espera tiene len 0,
    o bien vas a la fila

'''

# Importar demanda de carga
# Por ahora se esta suponiendo que el cargador es capaz de cargar a la potencia solicitada,
# y que todos los vehiculos demandan potencia de la misma forma
demanda_0 = pd.read_csv('Datos_entrada/Demanda_carga/prueba.csv')
# Crea una columna de tiempo en segundos y aproxima sus valores a enteros
demanda_0['tiempo [s]'] = demanda_0['tiempo [h]']*3600
for j in range(len(demanda_0['tiempo [s]'])):
    demanda_0['tiempo [s]'].iloc[j] = int(demanda_0['tiempo [s]'].iloc[j])


#autos que cargan por hora
n_hora = np.array([1,1,1,1,1,1,2,2, 2,3,4,4,4,5,5,5, 4,4,4,3,3,2,2,2])

# Info cargadores
n_rapidos = 6 # Sobre 22 kW
n_lentos = 3 # Bajo 22 kW

p_max_rapido = 150
p_max_lento = 22

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

# Creacion de cargadores lentos y rapidos con potencias maximas y estado desocupado por defecto
Rapidos, Lentos = crear_cargadores(n_rapidos,n_lentos, p_max_rapido, p_max_lento)

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
            Rapidos.iloc[i]['Estado'] == 1
            break
    
    return busqueda, c_rapido #, c_lento


lista_espera = [] # Podria contener info de carga del tipo [pot_carga_j, carga_solicitada_j (J), tiempo_carga_j]
demanda = []

#j para vehiculos, i para horas del dia
for i in range(len(n_hora)):
    if n_hora[i] != 0: # Evalua si la demanda es nula, sino debe ponerse a la lista
        # Anade cada demanda al vector lista de espera
        for j in range(n_hora[i]):
        # Esto deberia ser una distribucion para elegir vehiculos y sus caracteristicas
            demanda_auto_j = demanda_0[['Potencia [kW]', 'tiempo [s]', 'soc [%]']].copy()
            lista_espera.append(demanda_auto_j)
           
    while len(lista_espera) > 0:
        turno_j = lista_espera[0]
        t_total_carga = demanda_0['tiempo [s]'].iloc[-1] # en segundos
        match, cargador_j = buscar_cargador(Rapidos)
        
        if match == 1: # es decir, si encontro cargador
            demanda_j = turno_j # de la forma [p_carga_j, t_carga_j, soc_carga_j]
            demanda.append(demanda_j)
            # break
            del lista_espera[0]
        else:
            break # por ahora solo pasa a la hora siguiente si no hay cargadores
        # crear algoritmo de desocupado
    

