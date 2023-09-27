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

# Ruta del archivo TMY

# shit = pvlib.tmy.readtmy3('cebal\anaconda3\lib\site-packages\pvlib\data\DHTMY_E_T6854N.csv', coerce_year=None, recolumn=True)

#%%

# import pvlib
from pvlib import location
from pvlib import irradiance
from pvlib import tracking
from pvlib import solarposition
from pvlib.iotools import read_tmy3
import pandas as pd
from matplotlib import pyplot as plt
import pathlib
import numpy as np


latitude, longitude, tz =32.877394,	-117.233874, 'America/Los_Angeles'
surface_tilt = 10
surface_azimuth = 180 # pvlib uses 0=North, 90=East, 180=South, 270=West convention
albedo = 0.2

# specify time range.
start = pd.Timestamp(datetime.date.today(), tz='UTC') #00 UTC
end = start + pd.Timedelta(hours=36)
irrad_vars = ['ghi', 'dni', 'dhi']


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
i_sc_stc = 1
i_sc_p = G*(i_sc_stc)

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


def loctime (latitude, longitude, tz, altitude, place,\
             startdate, enddate,freq):
    loc = location(latitude, longitude, tz, altitude, place)
    time = pd.DatetimeIndex(start=startdate,end=enddate,freq,tz)
    return loc,time


def clearSky (time,loc):
    cs = loc.get_clearsky(time)
    return cs



#%%

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




