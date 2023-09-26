# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 09:13:51 2023

@author: cebal
"""

#%%### Nomenclatura ###
'''
a_p: area panel [m2]
az: angulo azimut [rad]
tilt: angulo de inclinacion [rad]
e_p: eficiencia panel [%]
i_a: corriente de un arreglo de paneles [A]
i_p: corriente de un panel [A]
i_in_i: corriente entrada inversor [A]
l1_p: largo panel [m]
l2_p: ancho panel [m]
r_p: radiacion sobre panel [W]
r_s: radiacion solar [W/m2]
th_p: inclinacion panel [rad]
v_a: voltaje de un arreglo de paneles [V]
v_p: voltaje de un panel [V]

_a: sufijo de arreglo de paneles
_p: sufijo panel
_i: sufijo inversor
_in: entrada
_c: sufijo cargador
_b: sufijo baterias
_out: salida
_s: sufijo solar

'''
#%%
import numpy as np
import pandas as pd
# import pvlib as pv
import matplotlib.pyplot as plt

import pvlib


#%%

# Ruta del archivo TMY

shit = pvlib.tmy.readtmy3('cebal\anaconda3\lib\site-packages\pvlib\data\DHTMY_E_T6854N.csv', coerce_year=None, recolumn=True)

#%%

import pvlib
from pvlib import location
from pvlib import irradiance
from pvlib import tracking
from pvlib.iotools import read_tmy3
import pandas as pd
from matplotlib import pyplot as plt
import pathlib

# get full path to the data directory
DATA_DIR = pathlib.Path(pvlib.__file__).parent / 'data'

# get TMY3 dataset
tmy, metadata = read_tmy3('pt06_iCeballos\DHTMY_E_T6854N.csv' coerce_year=1990)
# TMY3 datasets are right-labeled (AKA "end of interval") which means the last
# interval of Dec 31, 23:00 to Jan 1 00:00 is labeled Jan 1 00:00. When rolling
# up hourly irradiance to monthly insolation, a spurious January value is
# calculated from that last row, so we'll just go ahead and drop it here:
tmy = tmy.iloc[:-1, :]

# create location object to store lat, lon, timezone
location = location.Location.from_tmy(metadata)

# calculate the necessary variables to do transposition.  Note that solar
# position doesn't depend on array orientation, so we just calculate it once.
# Note also that TMY datasets are right-labeled hourly intervals, e.g. the
# 10AM to 11AM interval is labeled 11.  We should calculate solar position in
# the middle of the interval (10:30), so we subtract 30 minutes:
times = tmy.index - pd.Timedelta('30min')
solar_position = location.get_solarposition(times)
# but remember to shift the index back to line up with the TMY data:
solar_position.index += pd.Timedelta('30min')


# create a helper function to do the transposition for us
def calculate_poa(tmy, solar_position, surface_tilt, surface_azimuth):
    # Use the get_total_irradiance function to transpose the irradiance
    # components to POA irradiance
    poa = irradiance.get_total_irradiance(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        dni=tmy['DNI'],
        ghi=tmy['GHI'],
        dhi=tmy['DHI'],
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'],
        model='isotropic')
    return poa['poa_global']  # just return the total in-plane irradiance


# create a dataframe to keep track of our monthly insolations
df_monthly = pd.DataFrame()

# fixed-tilt:
for tilt in range(0, 50, 10):
    # we will hardcode azimuth=180 (south) for all fixed-tilt cases
    poa_irradiance = calculate_poa(tmy, solar_position, tilt, 180)
    column_name = f"FT-{tilt}"
    # TMYs are hourly, so we can just sum up irradiance [W/m^2] to get
    # insolation [Wh/m^2]:
    df_monthly[column_name] = poa_irradiance.resample('m').sum()

# single-axis tracking:
orientation = tracking.singleaxis(solar_position['apparent_zenith'],
                                  solar_position['azimuth'],
                                  axis_tilt=0,  # flat array
                                  axis_azimuth=180,  # south-facing azimuth
                                  max_angle=60,  # a common maximum rotation
                                  backtrack=True,  # backtrack for a c-Si array
                                  gcr=0.4)  # a common ground coverage ratio

poa_irradiance = calculate_poa(tmy,
                               solar_position,
                               orientation['surface_tilt'],
                               orientation['surface_azimuth'])
df_monthly['SAT-0.4'] = poa_irradiance.resample('m').sum()

# calculate the percent difference from GHI
ghi_monthly = tmy['GHI'].resample('m').sum()
df_monthly = 100 * (df_monthly.divide(ghi_monthly, axis=0) - 1)

df_monthly.plot()
plt.xlabel('Month of Year')
plt.ylabel('Monthly Transposition Gain [%]')
plt.show()

#%%

# Leer el archivo TMY
tmy_data, metadata = solarposition.get_solarposition(archivo_tmy, 32.2, -111)

# Extraer datos específicos
fechas = tmy_data.index
radiacion_directa = tmy_data['dni']
radiacion_diffusa = tmy_data['dhi']
radiacion_global = tmy_data['ghi']
temperatura_ambiente = tmy_data['temp_air']

# Realizar operaciones con los datos importados
# Por ejemplo, calcular la radiación total
radiacion_total = irradiance.get_total_irradiance(
    surface_tilt=20,
    surface_azimuth=180,
    solar_zenith=tmy_data['apparent_zenith'],
    solar_azimuth=tmy_data['azimuth'],
    dni=radiacion_directa,
    ghi=radiacion_global,
    dhi=radiacion_diffusa
)

# Imprimir algunos resultados
print("Fechas:", fechas)
print("Radiación total:", radiacion_total)
print("Temperatura ambiente:", temperatura_ambiente)


#%%
# Metodo pyephem y nrel son mas precisos, pero pyephem es mas rapido
 
times = pd.date_range('2014-01-01', '2015-01-01', freq='1h')
# ephem = pv.irradiance.get_extra_radiation(times, method='pyephem') 
nrel = pv.irradiance.get_extra_radiation(times, method='nrel', \
                                         solar_constant=1361)
nombre_ubicacion = 'Santiago'
ubicacion = pv.location.Location(32.2, -111, 'America/Santiago', 700, nombre_ubicacion)

posicion = ubicacion.get_solarposition(times)
irrad_data = ubicacion.get_clearsky(times)    
ground_irrad = pv.irradiance.get_ground_diffuse(40, irrad_data['ghi'], albedo=.25)

sun_zen = posicion['apparent_zenith']
sun_az = posicion['azimuth']
AM = pv.atmosphere.get_relative_airmass(sun_zen)

plt.plot(sun_az)


##%% Para utilizar radiacoin de albedo (fraccion reflejada por ambiente,suelo)  ~0.3 media
print(pv.irradiance.SURFACE_ALBEDOS.items())
superficies = pv.irradiance.SURFACE_ALBEDOS # superficies y radiacoin de albedo
l = ['sand','urban'] # 
result = list(map(superficies.get,l))
print(result)
suelo = pv.irradiance.get_ground_diffuse(40, irrad_data['ghi'], surface_type=superficies)

#%% FUNCION PARA EXTRAER RADIACION

# def get_total_irradiance_per_model(surface_tilt, surface_azimuth):
#     models = ['isotropic', 'klucher', 'haydavies', 'reindl', 'king', 'perez']
#     totals = {}

#     for model in models:
#         total = pv.irradiance.get_total_irradiance(
#             surface_tilt, surface_azimuth,
#             ephem_data['apparent_zenith'], ephem_data['azimuth'],
#             dni=irrad_data['dni'], ghi=irrad_data['ghi'], dhi=irrad_data['dhi'],
#             dni_extra=dni_et, airmass=AM,
#             model=model,
#             surface_type='urban')
#         totals[model] = total
#         total.plot()
#         plt.title(model)
#         plt.ylim(-50, 1100)
#         plt.ylabel('Irradiance (W/m^2)')

#     plt.figure()
#     for model, total in totals.items():
#         total['poa_global'].plot(lw=.5, label=model)

#     plt.legend()
#     plt.ylabel('Irradiance (W/m^2)')

#%%
dt = 1
tf = 3600
t = np.arange(0,tf+dt,dt)
n_t = len(t)


# area total disponible en terreno

a_total = 100

l1_p = 2
l2_p = 2
a_p = l1_p*l2_p
radiacion_test = 100
r_s = radiacion_test*np.ones(n_t)
r_p = r_s*a_p

G = 1
i_sc_p = G*(i_sc_stc)



# importar radiacion
# sacar inclinacion de paneles, incluyendo sus dimensiones y separacoin entre ellos
# con el area util ver cuantos paneles caben, estableecer numero de paneles
# tomar arreglo y construir paneles


