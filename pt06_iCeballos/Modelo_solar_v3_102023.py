# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 07:42:55 2023
@author: Nacho Ceballos
"""

# CALCULO CON TMY

from pvlib import location
from pvlib import irradiance
from pvlib import pvsystem
# from pvlib import inverter
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import pvlib
from datetime import datetime


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
    aoi.append(aoi_k)
    

# Importacion de modelo panel solar
sandia_modules = pvsystem.retrieve_sam('SandiaMod')
panel = sandia_modules['Kyocera_Solar_KD205GX_LP__2008__E__']

# CAMBIAR NANs por 0
# Crea una lista de OrderedDict, que pueden ser tratados como dataframes para extraer los valores
out_panel = []
v_out_panel = []
p_out_panel = []
for k in range(len(d_ghi)):
    # Extraccion de salida del panel con limpieza de nans
    k_ponderada = ghi[k]*np.cos(np.radians(aoi[k].iloc[0]))
    out_k = pd.Series(pvlib.pvsystem.sapm(k_ponderada, t_panel, panel))
    out_k.fillna(0,inplace=True)
    out_panel.append(out_k)
    # Calculo de voltaje y potencia de salida para cada hora
    v_out_k = out_k['v_mp']
    p_out_k = out_k['p_mp']
    v_out_panel.append(v_out_k)
    p_out_panel.append(p_out_k)
    
v_out_panel = np.array(v_out_panel)
p_out_panel = np.array(p_out_panel)

# Numero de paneles en serie y paralelo
ns = 15
np = 1

v_out_arreglo = ns*v_out_panel
p_out_arreglo = np*ns*p_out_panel

# Modulos con inversores
cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
#cols = [col for col in cec_inverters.columns if 'Xantrex' in col] # use this to look for strings in the catalog, it's huge
inversor = cec_inverters['Schneider_Electric_Solar_Inverters_USA___Inc___GT100_480__480V_']


# Devuelve potencia AC
p_ac = pvlib.inverter.sandia(v_out_arreglo, p_out_arreglo, inversor)

plt.figure()
plt.plot(v_out_panel)
plt.title('Voltaje un panel')

plt.figure()
plt.plot(p_out_panel)
plt.title('Potencia un panel')



plt.figure()
plt.plot(p_ac)
plt.ylabel('[W]')
plt.title('Potencia ac salida inversor')

# pvlib.inverter.sandia(v_dc, p_dc, inverter)



#%% PRODUCCION SIMPLIFICADA CON ECUACIONES SOLARES

# Creacion de ubicacion
tz = 'America/Santiago'
lat, lon = -33.4418, -70.7340
tilt_panel = 33
azimuth = 0 # pvlib uses 0=North, 90=East, 180=South, 270=West
ubicacion = location.Location(lat, lon, tz=tz)

# Calculate clear-sky GHI and transpose to plane of array
# Define a function so that we can re-use the sequence of operations with
# different locations
def get_irradiance(site_location, date, tilt, surface_azimuth):
    # Creates one day's worth of 10 min intervals
    times = pd.date_range(date, freq='10min', periods=6*24,
                          tz=site_location.tz)
    # Generate clearsky data using the Ineichen model, which is the default
    # The get_clearsky method returns a dataframe with values for GHI, DNI,
    # and DHI
    clearsky = site_location.get_clearsky(times)
    # Get solar azimuth and zenith to pass to the transposition function
    solar_position = site_location.get_solarposition(times=times)
    # Use the get_total_irradiance function to transpose the GHI to POA
    POA_irradiance = irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=surface_azimuth,
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'])
    # Return DataFrame with only GHI and POA
    return pd.DataFrame({'GHI': clearsky['ghi'],
                         'POA': POA_irradiance['poa_global']})


# Obtiene la irradiancia para solsticios de veranos e invierno
verano = get_irradiance(ubicacion,'12-21-2020', tilt_panel, azimuth)
invierno = get_irradiance(ubicacion, '06-20-2020', tilt_panel, azimuth)


verano_np = verano.to_numpy()
invierno_np = invierno.to_numpy()

ef_p = 0.2
l1, l2 = 1, 2
area = l1*l2 

rad_verano, rad_invierno =  np.transpose(verano_np)[1]*area, np.transpose(invierno_np)[1]*area
pot_verano, pot_invierno = rad_verano*ef_p, rad_invierno*ef_p

ef_inv = 0.95

p_elec_verano, p_elec_invierno = ef_inv*pot_verano, pot_invierno*ef_inv


plt.figure()
plt.grid()
plt.plot(p_elec_verano)
plt.plot(p_elec_invierno)
plt.xlabel('Hora del día')
plt.ylabel('Potencia eléctrica generada [W]')
plt.title('Generación día de verano')
plt.legend(['Día de verano', 'Día de invierno'])
plt.show()

#%% DESCRIPCION VARIABLES PANELES

# A0-A4
# The airmass coefficients used in calculating effective irradiance
# B0-B5
# The angle of incidence coefficients used in calculating effective irradiance
# C0-C7
# The empirically determined coefficients relating Imp, Vmp, Ix, and Ixx to effective irradiance
# Isco
# Short circuit current at reference condition (amps)
# Impo
# Maximum power current at reference condition (amps)
# Voco
# Open circuit voltage at reference condition (amps)
# Vmpo
# Maximum power voltage at reference condition (amps)
# Aisc
# Short circuit current temperature coefficient at reference condition (1/C)
# Aimp
# Maximum power current temperature coefficient at reference condition (1/C)
# Bvoco
# Open circuit voltage temperature coefficient at reference condition (V/C)
# Mbvoc
# Coefficient providing the irradiance dependence for the BetaVoc temperature coefficient at reference irradiance (V/C)
# Bvmpo
# Maximum power voltage temperature coefficient at reference condition
# Mbvmp
# Coefficient providing the irradiance dependence for the BetaVmp temperature coefficient at reference irradiance (V/C)
# N
# Empirically determined “diode factor” (dimensionless)
# Cells_in_Series
# Number of cells in series in a module’s cell string(s)
# IXO
# Ix at reference conditions
# IXXO
# Ixx at reference conditions
# FD
# Fraction of diffuse irradiance used by module

#%%

# Paco
# AC power rating of the inverter. [W]
# Pdco
# DC power input that results in Paco output at reference voltage Vdco. [W]
# Vdco
# DC voltage at which the AC power rating is achieved with Pdco power input. [V]
# Pso
# DC power required to start the inversion process, or self-consumption by inverter, strongly influences inverter efficiency at low power levels. [W]
# C0
# Parameter defining the curvature (parabolic) of the relationship between AC power and DC power at the reference operating condition. [1/W]
# C1
# Empirical coefficient allowing Pdco to vary linearly with DC voltage input. [1/V]
# C2
# Empirical coefficient allowing Pso to vary linearly with DC voltage input. [1/V]
# C3
# Empirical coefficient allowing C0 to vary linearly with DC voltage input. [1/V]
# Pnt
# AC power consumed by the inverter at night (night tare). [W]