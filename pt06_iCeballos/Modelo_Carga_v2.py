# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 11:23:48 2023

@author: Nacho
"""

import numpy as np
import pandas as pd

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

# Importacion demanda de carga
# Por ahora se esta suponiendo que elcargador es capaz de cargar, y que todos los vehiculos
# demandan potencia de la misma forma
demanda_0 = pd.read_csv('Datos_entrada/Demanda_carga/prueba.csv')
#%%

#autos que cargan por hora
n_hora = np.array([1,1,1,1,1,1,2,2, 2,3,4,4,4,5,5,5, 4,4,4,3,3,2,2,2])
    
# #potencia requerida por cada vehiculo kW
# dist_carga = np.array([22.4,44.6])

# #capacidad de banco de baterias de vehiculo kWh
# capacidad = np.array([20, 40, 60]) # por ahora corresponde a lo que van a cargar, no al total de lo que pueden cargar

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
        rapidos.loc[nombre_j] = [0, p_lentos]
    
    lentos = pd.DataFrame([], columns=['Estado','Potencia maxima'])
    for i in range(n_lentos):
        nombre_i = 'Lento '+ str(i)
        lentos.loc[nombre_i] = [0, p_lentos]
        
    return rapidos, lentos

#Creacion de cargadores lentos y rapidos con potencias maximas y estado desocupado por defecto
Rapidos, Lentos = crear_cargadores(n_rapidos,n_lentos, p_max_rapido, p_max_lento)

def buscar_cargador(Rapidos, Lentos):
    '''
    Busca un cargador para el vehiculo que solicita carga, devolviendo si hay cargador
    disponible con busqueda=1, y en c_rapido o c_lento el indice del cargador asignado
    Si busqueda=0 se seguira cno otro algoritmo para otorgar un lugar en la fila
    '''
    busqueda = 0
    c_rapido = 0
    c_lento = 0
    
    for i in range(len(Rapidos)):
        if Rapidos.iloc[i]['Estado'] == 0:
            busqueda = 1
            c_rapido = i
            Rapidos.iloc[i]['Estado'] == 1
            break
    if busqueda == 0:
        for i in range(len(Lentos)):
            if Lentos.iloc[i]['Estado'] == 0:
                busqueda = 1
                c_lento = i
                Lentos.iloc[i]['Estado'] == 1
                break
    
    return busqueda, c_rapido, c_lento

def carga(t_carga, p_carga):
    '''
    Funcion ultra simplista para establecer la potencia de carga
    '''
    pot_carga = p_carga*np.ones(t_carga)
    volt_carga = 10*np.ones(t_carga)
    return pot_carga#, volt_carga

lista_espera = [] # contiene info de carga del tipo [pot_carga_j, carga_j, tiempo_carga_j]
demanda = []

#%%

for i in range(len(n_hora)):
    if n_hora[i] != 0:
        for j in range(len(n_hora[i])):
        
        demanda_j = [] # vector demanda de cada auto
        # toda esta parte debera ser reemplazada al integra lo de EK
        pot_carga_j = np.random.choice(dist_carga) # eleccoines aleatorias para la potencia maxima de carga y 
        carga_j = np.random.choice(capacidad) # la capacidad de almacenamiento
        tiempo_carga_j =  3600*carga_j/pot_carga_j # en segundos    
        
            lista_espera.append(n_hora[i]) #[pot_carga_j, carga_j, tiempo_carga_j]
                
        
        
        
    for j in range(n_hora[i]):
    
    # Caso1: no hay demanda ni autos en la lista de espera
    if n_hora[i] ==0 and len(lista_espera) == 0:
        print('No hay demanda a esta hora')
        
    # Caso2: no hay demanda pero si hay lista de espera
    elif n_hora[i] == 0 and len(lista_espera) != 0:
        # correr lista de espera
        print('correr lista de espera, algoritmo en proceso')
        
        
        demanda_j = [] # vector demanda de cada auto
        # toda esta parte debera ser reemplazada al integra lo de EK
        pot_carga_j = np.random.choice(dist_carga) # eleccoines aleatorias para la potencia maxima de carga y 
        carga_j = np.random.choice(capacidad) # la capacidad de almacenamiento
        tiempo_carga_j =  3600*carga_j/pot_carga_j #en segundos
        
        potencia
        
    # Caso3: hay demanda pero no hay lista de espera
    else:
        for j in range(n_hora[i]):
            
            demanda_j = [] # vector demanda de cada auto
            # toda esta parte debera ser reemplazada al integra lo de EK
            pot_carga_j = np.random.choice(dist_carga) # eleccoines aleatorias para la potencia maxima de carga y 
            carga_j = np.random.choice(capacidad) # la capacidad de almacenamiento
            tiempo_carga_j =  3600*carga_j/pot_carga_j #en segundos
            
            '''
            Aca comienza el algoritmo para elegir cargador, queda a la lista de espera, etc
            '''
            disponible, n_lento, n_rapido = buscar_cargador(Rapidos, Lentos)
            
            
            if disponible == 1 and len(lista_espera) == 0:
                # Si hay cargador disponible, se establece si este es rapido o lento, se calcula la funcion demanda de potencia
                # y luego se crea una lista demanda para cada auto, que contiene el vector demanda, la hora de inicio de carga y
                # el cargador usado
                n_usado = max(n_lento, n_rapido)
                demanda_j = carga(tiempo_carga_j, pot_carga_j)
                demanda.append([demanda_j, i, n_usado])
            elif:
                lista_espera.append([pot_carga_j, carga_j, tiempo_carga_j])
            
        
        
        potencia, voltaje = carga(tiempo_carga_i)




#%%
for i in range(len(n_hora)):
    # Caso1: no hay demanda ni autos en la lista de espera
    if n_hora[i] ==0 and len(lista_espera) == 0:
        print('No hay demanda a esta hora')
        
    # Caso2: no hay demanda pero si hay lista de espera
    elif n_hora[i] == 0 and len(lista_espera) != 0:
        # correr lista de espera
        print('correr lista de espera, algoritmo en proceso')
        
        
        demanda_j = [] # vector demanda de cada auto
        # toda esta parte debera ser reemplazada al integra lo de EK
        pot_carga_j = np.random.choice(dist_carga) # eleccoines aleatorias para la potencia maxima de carga y 
        carga_j = np.random.choice(capacidad) # la capacidad de almacenamiento
        tiempo_carga_j =  3600*carga_j/pot_carga_j #en segundos
        
        potencia
        
    # Caso3: hay demanda pero no hay lista de espera
    else:
        for j in range(n_hora[i]):
            
            demanda_j = [] # vector demanda de cada auto
            # toda esta parte debera ser reemplazada al integra lo de EK
            pot_carga_j = np.random.choice(dist_carga) # eleccoines aleatorias para la potencia maxima de carga y 
            carga_j = np.random.choice(capacidad) # la capacidad de almacenamiento
            tiempo_carga_j =  3600*carga_j/pot_carga_j #en segundos
            
            '''
            Aca comienza el algoritmo para elegir cargador, queda a la lista de espera, etc
            '''
            disponible, n_lento, n_rapido = buscar_cargador(Rapidos, Lentos)
            
            
            if disponible == 1 and len(lista_espera) == 0:
                # Si hay cargador disponible, se establece si este es rapido o lento, se calcula la funcion demanda de potencia
                # y luego se crea una lista demanda para cada auto, que contiene el vector demanda, la hora de inicio de carga y
                # el cargador usado
                n_usado = max(n_lento, n_rapido)
                demanda_j = carga(tiempo_carga_j, pot_carga_j)
                demanda.append([demanda_j, i, n_usado])
            elif:
                lista_espera.append([pot_carga_j, carga_j, tiempo_carga_j])
            
        
        
        potencia, voltaje = carga(tiempo_carga_i)
        
        
    
    
    
    
    
    
    



        
    
    
    
    









