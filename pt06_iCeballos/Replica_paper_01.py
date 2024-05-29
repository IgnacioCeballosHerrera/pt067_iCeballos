# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 11:53:01 2024

@author: Nacho
"""

''' MODELO PARA PREDICCION DE DEMANDA '''
import random
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as ss
import glob
import pandas as pd
import random
from scipy import interpolate 

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


def extraer_demandas(dataframe_autos):
    '''
    Toma el datafrmae de distintas cargas
    '''
    demandas = []
    for j in range(len(dataframe_autos)):
        demanda_0 = dataframe_autos[j]
        demanda_0['tiempo [min]'] = demanda_0['tiempo [h]']*60
        for j in range(len(demanda_0['tiempo [min]'])):
            demanda_0['tiempo [min]'].iloc[j] = int(demanda_0['tiempo [min]'].iloc[j])
        demandas.append(demanda_0)
    return demandas

def generar_demanda(parametros, tipo):
    '''
    Genera un tiempo hasta la proxima demanda basado en los parametros de la
    distribucion escogida 
    '''
    
    if tipo == 'normal':
        lamda, sd = parametros
        x= random.normalvariate(lamda, sd)
    elif tipo == 'weibull':
        alfa, beta = parametros
        x = random.weibullvariate(alfa, beta)
    return x

# tiempo espera promedio en minutos por hora
lamda_hora = np.array([30,30,30,30,30,30,15,15, 15,15,15,15,15,15,15,15, 15,15,15,15,15,30,30,30])
tiempo_horas = np.arange(0, 24, 1/(60))


''' Demanda de carga '''

i = 1
i_vector = [1]
dt_vector = []

# Generacion aleatoria de eventos de demanda
while i < 60*24:
    lamda_i = lamda_hora[int(i/60)]
    dt = generar_demanda([lamda_i, lamda_i*0.3], 'normal')
    dt_vector.append(dt)
    i = i + dt
    i_vector.append(i)
  
#%% GRAFICOS DE CASO SIMPLE
plt.figure()
plt.title('Eventos de demanda durante el día')
plt.plot(i_vector)
plt.show()

plt.figure()
plt.title('Tiempos de espera entre cargas')
plt.plot(dt_vector)
plt.show()
    
# plt.figure(figsize = (8, 4))
# plt.hist(dt_vector, 50)
# plt.title('Distribución de tiempos de carga')
# plt.grid()
# plt.show()

plt.figure(figsize = (8, 4))
plt.hist(i_vector, 50)
plt.title('Distribucion de eventos de carga')
plt.grid()
plt.show()

# plt.figure()
# plt.title('Distribución horaria de carga promedio')
# plt.plot(lamda_hora)
# plt.ylim(0,40)
# plt.grid()
# plt.show()
#%%

dt_montecarlo = []
event_montecarlo = []
for j in range(1000):
    print(j)
    i_vector = []
    dt_vector = []
    i_ref = 0
    for i in range(60*24):
        if i == i_ref:
            lamda_i = lamda_hora[int(i/60)]
            dt = generar_demanda([lamda_i, lamda_i*0.3], 'normal')
            i_ref = int(i + dt)
            i_vector.append(i)
            dt_vector.append(dt)
        else:
            i_vector.append(0)
            dt_vector.append(0)

    dt_montecarlo.append(dt_vector)
    event_montecarlo.append(i_vector)


dt_montecarlo = np.array(dt_montecarlo)
event_montecarlo = np.array(event_montecarlo)

event_mean = np.average(event_montecarlo, axis= 0)
dt_mean = np.average(dt_montecarlo, axis= 0)


#%% GRAFICOS MONTECARLO
# plt.figure()
# plt.plot(tiempo_horas, event_mean)
# plt.title('Promedio de ocurrencia demanda')
# plt.xlabel('Horas del día')
# plt.ylabel('Promedio de ocurrencia demanda')
# plt.show()

# plt.figure()
# plt.plot(dt_mean)
# plt.ylim(0,15)
# plt.title('Promedio de tiempo de espera')
# plt.show()
#%%
''' Estados de carga iniciales '''

# PARA USAR CAPACIDAD POR ESTEBAN
# directorio_carpeta = 'Datos_entrada/Demanda_carga'
# df_autos = extraer_csvs(directorio_carpeta)
# df_demandas = extraer_demandas(df_autos)

# PARA USAR DEMANDA PAPER
df_battery = pd.DataFrame([[3.6,0.115,0.115], [16,0.37, 0.485] ,[25,0.380,0.865], [63,0.135,1]], \
                columns = ['Battery capacity [kWh]','Probability (%)', 'Accumulated probability (%)'],\
                index= ['Bike', 'Small private car','Large private car', 'Van'])

# Prueba paper Dominguez

plt.figure()

# Creacion de datos aleatorios]
mu, sigma = 3, 0.6 # media y sd
dist_trav = np.random.lognormal(mu, sigma, 1000)
count, bins, ignored = plt.hist(dist_trav, 100, density=True, align='mid')

# Pdf de distancias recorridas
x = np.linspace(min(bins), max(bins), 10000)
SOC = (np.exp(-(np.log(x) - mu)**2 / (2 * sigma**2)) / (x * sigma * np.sqrt(2 * np.pi)))

# plt.figure()
plt.plot(x, SOC, linewidth=2, color='r')
plt.axis('tight')
plt.show()

#MIENTRAS TANTO#!!!
P_charger = 20
Battery_capacity = 25

t_charge = Battery_capacity*(1- SOC)/P_charger

# Falta asignar esta carga a algun cargador
#%%
''' Generacion  eolica'''

# Importar curvas de potencia: b:tipo1, r:tipo2, y:tipo3
r = pd.read_csv('Datos_entrada/Paper estacion de carga/curva_roja.csv', header = None)
r.columns =['Velocidad [m/s]','Potencia [kW]']
b = pd.read_csv('Datos_entrada/Paper estacion de carga/curva_azul.csv', header = None)
b.columns =['Velocidad [m/s]','Potencia [kW]']
y = pd.read_csv('Datos_entrada/Paper estacion de carga/curva_amarilla.csv', header = None)
y.columns =['Velocidad [m/s]','Potencia [kW]']

v_lim = [(min(b['Velocidad [m/s]']), max(b['Velocidad [m/s]'])) ,\
         (min(r['Velocidad [m/s]']), max(r['Velocidad [m/s]'])) ,\
             (min(y['Velocidad [m/s]']), max(y['Velocidad [m/s]']))]

plt.figure()
plt.xlabel('Velocidad del viento [m/s]')
plt.ylabel('Potencia [kW]')
plt.plot(r['Velocidad [m/s]'], r['Potencia [kW]'], color = 'r')
plt.plot(b['Velocidad [m/s]'], b['Potencia [kW]'], color = 'b')
plt.plot(y['Velocidad [m/s]'], y['Potencia [kW]'], color = 'y')
plt.show()

# Funciones para interpolar los datos de potencia segun cada curva
r_inter = interpolate.interp1d(r['Velocidad [m/s]'], r['Potencia [kW]'], kind = 'linear')
b_inter = interpolate.interp1d(b['Velocidad [m/s]'], b['Potencia [kW]'], kind = 'linear')
y_inter = interpolate.interp1d(y['Velocidad [m/s]'], y['Potencia [kW]'], kind = 'linear')

vm = 6 # m/s
k = 2 #alfa
c = vm*(0.568 + (0.433/k))**(-1/k) #beta
v_hora = [random.weibullvariate(c, k) for i in range(24)] # generacion aleatoria por weibull

# Para probar los parametros de la curva
# v = np.arange(0,30,0.1) # vector velocidades
# pdf_v = (k/c)*((v/c)**(k-1))*np.exp(-(v/c)**k)*10000
# pdf_cum_v = np.cumsum(list(pdf_v))*0.1 # para comprobar la probabilidad
# print('Pdf de velocidad acumulada es:', pdf_cum_v)
# plt.figure()
# plt.plot(v, pdf_v)
# plt.show()


def velocidad_weibull(c, k, tipo_turbina, largo):
    '''
    Genera un vector de velociddades que distribuyen weibull, con cierto largo
    y adaptado a los limites de la turbina. 
    
    c,k: parámetros de distribucion weibull
    tipo: El tipo de la turbinadebe ser el numero asociado a ella segun paper
    largo: largo deseado del vector velocidad a generar
    '''
    velocidades = []
    for i in range(24):
        v_azar = random.weibullvariate(c, k)
        while v_azar<v_lim[tipo_turbina-1][0] or v_azar>v_lim[tipo_turbina-1][1]: #excede valores limites
            v_azar = random.weibullvariate(c, k)
        velocidades.append(v_azar)
    return velocidades

vel_test= velocidad_weibull(c,k,1, 24)

#correcion para que este dentro de los limites



plt.figure()
plt.xlabel('Hora del día [hrs]')
plt.ylabel('Velocidad del viento [m/s]')
plt.plot(v_hora)
plt.show()
# Para comprobar que distribuye weibull
# plt.figure(figsize = (8, 4))
# plt.hist(v_hora, bins = 100)
# plt.grid()
# plt.show()




p_eolica = r_inter(v_hora) #potencia eolica generada de prueba 

# v_2 = -c*(np.log(1-list_weibull))**(1/k)

# plt.figure()
# plt.plot(list_weibull)
# plt.show()