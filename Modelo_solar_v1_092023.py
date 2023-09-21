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
import pvlib as pv
import matplotlib.pyplot as plt


# dt = 1
# tf = 3600
# t = np.arange(0,tf+dt,dt)
# n_t = len(t)

# Metodo pyephem y nrel son mas precisos, pero pyephem es mas rapido
 
times = pd.date_range('2014-01-01', '2015-01-01', freq='1h')
# ephem = pv.irradiance.get_extra_radiation(times, method='pyephem') 
nrel = pv.irradiance.get_extra_radiation(times, method='nrel', \
                                         solar_constant=1361)
nombre_ubicacion = 'Santiago'
ubicacion = pv.location.Location(32.2, -111, 'America/Santiago', 700, nombre_ubicacion)

nrel_data = ubicacion.get_solarposition(times)
irrad_data = ubicacion.get_clearsky(times)    
ground_irrad = pv.irradiance.get_ground_diffuse(40, irrad_data['ghi'], albedo=.25)

sun_zen = nrel_data['apparent_zenith']
sun_az = nrel_data['azimuth']
AM = pv.atmosphere.get_relative_airmass(sun_zen)


##%%
print(pv.irradiance.SURFACE_ALBEDOS.items())
superficies = pv.irradiance.SURFACE_ALBEDOS
l = ['sand','urban']
result = list(map(superficies.get,l))
print(result)
# print(superficies)
# suelo = pv.irradiance.get_ground_diffuse(40, irrad_data['ghi'], surface_type=superficies)

#%%

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

# area total disponible en terreno

a_total = 100

l1_p = 2
l2_p = 2
a_p = l1_p*l2_p
radiacion_test = 100
r_s = radiacion_test*np.ones(n_t)
r_p = r_s*a_p







