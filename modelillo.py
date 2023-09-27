# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 07:42:55 2023

@author: Nacho
"""

from pvlib import location
from pvlib import irradiance
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

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
# Convierte los valores de indices a horas: minutos para hacerlos mas entendible
# verano.index = verano.index.strftime("%H:%M")
# invierno.index = invierno.index.strftime("%H:%M")

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


#%%
# Plot GHI vs. POA for winter and summer
# fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
# verano['GHI'].plot(ax=ax1, label='GHI')
# verano['POA'].plot(ax=ax1, label='POA')
# invierno['GHI'].plot(ax=ax2, label='GHI')
# invierno['POA'].plot(ax=ax2, label='POA')
# ax1.set_xlabel('Día de Verano')
# ax2.set_xlabel('Día de invierno')
# ax1.set_ylabel('Irradiancia ($W/m^2$)')
# ax1.legend()
# ax2.legend()
# plt.show()
#%%
