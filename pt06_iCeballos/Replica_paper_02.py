# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 11:53:01 2024

@author: Nacho
"""

''' MODELO PARA PREDICCION DE DEMANDA '''
import random
import numpy as np
import matplotlib.pyplot as plt
# import scipy.stats as ss
import pandas as pd
# import random
from scipy import interpolate
import pvlib
from datetime import datetime


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

# Lamda es tiempo de espera promedio de llegada de cada auto despues de un auto
# depende de la hora del dia y el que esta aca es el del paper
lamda_hora = np.array([30,30,30,30,30,30,15,15, 15,15,15,15,15,15,15,15, 15,15,15,15,15,30,30,30])
tiempo_horas = np.arange(0, 24, 1/(60))


''' Demanda de carga '''
i = 1
k_sd = 0.3 # coeficiente para obtener desviacion estandar respecto a la normal 
i_vector = [] # vector que guarda el minuto del dia donde ocurre una demanda i
dt_vector = [] # vector que guarda la espera entre demanda y demanda

# Generacion aleatoria de eventos de demanda
while i < 60*24:
    lamda_i = lamda_hora[int(i/60)]
    dt = generar_demanda([lamda_i, lamda_i*0.3], 'normal')
    dt_vector.append(dt)
    i = i + dt
    i_vector.append(i)
  
##%% GRAFICOS DE CASO SIMPLE
plt.figure()
plt.title('Eventos de demanda durante el día')
plt.plot(i_vector)
plt.show()

plt.figure()
plt.title('Tiempos de espera entre cargas')
plt.xlabel('Eventos de carga ')
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
# #%%

# dt_montecarlo = []
# event_montecarlo = []
# for j in range(1000):
#     print(j)
#     i_vector = []
#     dt_vector = []
#     i_ref = 0
#     for i in range(60*24):
#         if i == i_ref:
#             lamda_i = lamda_hora[int(i/60)]
#             dt = generar_demanda([lamda_i, lamda_i*0.3], 'normal')
#             i_ref = int(i + dt)
#             i_vector.append(i)
#             dt_vector.append(dt)
#         else:
#             i_vector.append(0)
#             dt_vector.append(0)

#     dt_montecarlo.append(dt_vector)
#     event_montecarlo.append(i_vector)


# dt_montecarlo = np.array(dt_montecarlo)
# event_montecarlo = np.array(event_montecarlo)

# event_mean = np.average(event_montecarlo, axis= 0)
# dt_mean = np.average(dt_montecarlo, axis= 0)


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

def velocidad_weibull(c, k, tipo_turbina, largo):
    '''
    Genera un vector de velociddades que distribuyen weibull, con cierto largo
    y adaptado a los limites de la turbina. 
    
    c,k: parámetros de distribucion weibull.
    tipo: El tipo de la turbinadebe ser el numero asociado a ella segun paper,
          con b:tipo1, r:tipo2, y:tipo3.  
    largo: largo deseado del vector velocidad a generar.
    '''
    velocidades = []
    for i in range(24):
        v_azar = random.weibullvariate(c, k)
        while v_azar<v_lim[tipo_turbina-1][0] or v_azar>v_lim[tipo_turbina-1][1]: #excede valores limites
            v_azar = random.weibullvariate(c, k)
        velocidades.append(v_azar)
    return velocidades

# distribucion de velocidad y potencia horaria
v_hora = velocidad_weibull(c,k,2,1000) 
p_wind_hora = r_inter(v_hora)
horas = np.arange(24)

fig, axes = plt.subplots()
axes.plot(horas, v_hora, color='b')
axes.set_xlabel('Hora del dia [hrs]')
axes.set_ylabel('Velocidad del viento [m/s]', color='b')
twin_axes = axes.twinx() 
twin_axes.plot(horas,p_wind_hora, 'r')
twin_axes.set_ylabel('Potencia eolica generada [kW]', color='r')
plt.title('Modelamiento para un día de generacion Eolica')
plt.show()

# Para comprobar que velocidad distribuye weibull
plt.figure(figsize = (8, 4))
plt.hist(v_hora, bins = 100)
plt.grid()
plt.show()
#%%
'''  Generacion solar '''

# Fecha escogida
mes = 12
dia = 12
# Datos de panel
tilt = 10
az = 180
t_panel = 25

# Importacion y lectura de TMY (PARA FORMATO EXPLORADOR SOLAR)
archivo_tmy = 'pt067_iCeballos/pt06_iCeballos/DHTMY_E_T6854N.csv'
data_tmy = pd.read_csv(archivo_tmy, skiprows = 41)
location_tmy = pd.read_csv(archivo_tmy, skiprows = 11, skipfooter = 8802-14,\
                           header = None, engine = 'python')
description_tmy = pd.read_csv(archivo_tmy,skiprows = 25, skipfooter = 8802-38,\
                              engine = 'python')

# Extraccion de valores ambientales
times = data_tmy['Fecha/Hora'].to_numpy()
ghi = data_tmy['ghi'].to_numpy()
cloud = data_tmy['cloud'].to_numpy()
temperature = data_tmy['temp'].to_numpy()
velocity = data_tmy['vel'].to_numpy()
shadow = data_tmy['shadow'].to_numpy()

# Extraccion de datos ubicacion
latitud = location_tmy[1][0]
longitud = location_tmy[1][1]
altitud = location_tmy[1][2]

# Loop para la extraccion de datos para la fecha solicitada (dia y mes)
for i in range(len(times)):
    date_str = times[i]
    date_format = '%Y-%m-%d %H:%M:%S'
    fecha = datetime.strptime(date_str, date_format)
    # year = fecha.year
    month = fecha.month
    day = fecha.day
    if month == mes and day == dia:
        d_ghi = ghi[i:i+24]
        d_date = times[i:i+24]
        d_cloud = cloud[i:i+24]
        d_temp = temperature[i:i+24]
        d_vel = velocity[i:i+24]
        d_sh = shadow[i:i+24]
        break

# Loop para conocer el angulo de incidencia sobre panel en cada instante
sol_pos = [] # Sera una lista con dataframes
aoi = [] # Angulo de incidencia entre panel y radiacion solar
for k in d_date:
    # Para obtener posicion solar
    sol_pos_k = pvlib.solarposition.get_solarposition(k, latitud, longitud,\
                altitud, pressure=None, method='nrel_numpy', temperature=12)
    # Para obtener angulo de incidencia 
    aoi_k = pvlib.irradiance.aoi(tilt, az, sol_pos_k['zenith'],\
                                                         sol_pos_k['azimuth'])
    sol_pos.append(sol_pos_k)
    aoi.append(aoi_k[0])


G = d_ghi*abs(np.cos(aoi))

plt.figure()
plt.title('Radiación global horizontal en el dia seleccionado')
plt.ylabel('Hora del día [hrs]')
plt.xlabel('Radiación global horizontal [W/m2]')
plt.plot(G)
plt.show()
    
#%%

import pygad
import numpy

function_inputs = [4,-2,3.5,5,-11,-4.7]
desired_output = 44

def fitness_func(ga_instance, solution, solution_idx):
    output = numpy.sum(solution*function_inputs)
    fitness = 1.0 / numpy.abs(output - desired_output)
    return fitness

fitness_function = fitness_func

num_generations = 50
num_parents_mating = 4

sol_per_pop = 8
num_genes = len(function_inputs)

init_range_low = -2
init_range_high = 5

parent_selection_type = "sss"
keep_parents = 1

crossover_type = "single_point"

mutation_type = "random"
mutation_percent_genes = 10

##%%
ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_function,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       init_range_low=init_range_low,
                       init_range_high=init_range_high,
                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents,
                       crossover_type=crossover_type,
                       mutation_type=mutation_type,
                       mutation_percent_genes=mutation_percent_genes)

##%%
'''
num_generations = numero de iteraciones
num_parents_mating = numero de soluciones a seleccionar como padres 
fitness_func =
sol_per_pop = numero de cromosomas en la poblacion
num_genes = numero de genes en el cromosoma
init_range_low= The lower value of the random range from which the gene values 
                in the initial population are selected. 
init_range_high=Lo mismo de arriba pero limite superior

parent_selection_type=parent_selection_type,
keep_parents=keep_parents,
crossover_type=crossover_type,
mutation_type=mutation_type,
mutation_percent_genes=mutation_percent_genes)
'''

'''
PAPER:
    


'''



ga_instance.run()
#%%
solution, solution_fitness, solution_idx = ga_instance.best_solution()
print("Parameters of the best solution : {solution}".format(solution=solution))
print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))

prediction = numpy.sum(numpy.array(function_inputs)*solution)
print("Predicted output based on the best solution : {prediction}".format(prediction=prediction))