'''
Prueba de niveles de corriente y torque para flota Evs
'''


import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% FUNCION EXTRAER CSV
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
#%%
# Define la ruta de la carpeta que contiene archivos CSV.
directorio_carpeta = 'DataBuses_v2/C_abril_2020_v2'
df_viajes = extraer_csvs(directorio_carpeta)

potencia_con = np.zeros(0)
potencia_gen = np.zeros(0)
velocidades = np.zeros(0)

for i in df_viajes:
    p_cons = i['Potencia Total Consumida']
    p_gen = i['Potencia Total Generada']
    vel = i['Velocidad']
    
    vel = np.array(vel)
    p_gen = np.array(p_gen)
    p_cons = np.array(p_cons)
    
    potencia_con = np.append(potencia_con, p_cons)
    potencia_gen = np.append(potencia_gen, p_gen)
    velocidades = np.append(velocidades , vel)

radio_neu = 0.25
ef = 0.9

potencia_neta = potencia_con + potencia_gen
v_angulares = velocidades/radio_neu

torque = ef*potencia_neta/v_angulares
torque[torque == np.inf] = np.nan
torque[torque == -np.inf] = np.nan

plt.plot(torque)
# constantes para eficiencia del vehiculo
c = 20
k_w = 10e-5 # perdidas por friccion de viento
k_i = 0.1 # perdidas por hierro (magneticas)
k_c = 0.8 #peridas por cobre (electricas)
 
#%% FUNCION DE EFICIENCIA
def eficiencia(torque, omega):
    '''
    Calcula la eficiencia para un estado de torque y una velodidad angular
    en un motor de modelo magnetico simple con esobillas
    '''
    t = torque
    w = omega
    ef = (t*w) / (t*w + k_w*(w**3) + k_i*w + k_c*(t**2) + c)
    return ef
#%%

v_angulares = np.arange(5,50,5)
torques = np.arange(10,200,10)
ef_tot = []
for i in range(len(torques)):
    ef_i = []
    for k in range(len(v_angulares)):
        ef_k = eficiencia(torques[i], v_angulares[k])
        ef_i.append(ef_k)
    ef_tot.append(ef_i)
    
eficiencias = pd.DataFrame(ef_tot)
efc = np.array(ef_tot)

# plt.figure()
# plt.plot(corrientes)
# plt.ylabel('Corriente [A]')
# plt.xlabel('Viajes concatenados')

    
    