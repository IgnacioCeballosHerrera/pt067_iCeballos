# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 07:42:55 2023

@author: Nacho
"""

from pvlib import location
from pvlib import irradiance
from pvlib import pvsystem
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from Tmy_reader import readtmy2
import pvlib
from datetime import datetime

# Importacion de TMY
archivo_tmy = 'DHTMY_E_T6854N.csv'
data_tmy = pd.read_csv(archivo_tmy, skiprows = 41)
location_tmy = pd.read_csv(archivo_tmy, skiprows = 11, skipfooter = 8802-14, header = None, engine = 'python')
description_tmy = pd.read_csv(archivo_tmy, skiprows = 25, skipfooter = 8802-38, engine = 'python')

# Extraccion de valores ambientales
times = data_tmy['Fecha/Hora']
ghi = data_tmy['ghi'].to_numpy()
cloud = data_tmy['cloud'].to_numpy()
temp = data_tmy['temp'].to_numpy()
vel = data_tmy['vel'].to_numpy()
shadow = data_tmy['shadow'].to_numpy()

# Usar esto en modo iterativo para cambiar de str a datetime todos los objetos en la serie times
date_str = times[0]
date_format = '%Y-%m-%d %H:%M:%S'
date_obj = datetime.strptime(date_str, date_format)
print(date_obj)

# Modulos con paneles solares
sandia_modules = pvsystem.retrieve_sam('SandiaMod')
module = sandia_modules['Kyocera_Solar_KD205GX_LP__2008__E__']

cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
#cols = [col for col in cec_inverters.columns if 'Xantrex' in col] # use this to look for strings in the catalog, it's huge
inverter=cec_inverters['Schneider_Electric_Solar_Inverters_USA___Inc___GT100_480__480V_']

#%% Desde codigo monica zamora, importacion de librerias


cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
#cols = [col for col in cec_inverters.columns if 'Xantrex' in col] # use this to look for strings in the catalog, it's huge
#inverter = cec_inverters['Xantrex_Technologies__Inc___GT100_480_480V__CEC_2007_']
inverter=cec_inverters['Schneider_Electric_Solar_Inverters_USA___Inc___GT100_480__480V_']
system = pvsystem.PVSystem(surface_tilt=10, surface_azimuth=180,
                  module_parameters=module,
                  inverter_parameters=inverter) #only takes one single module

#specify 2 inverters with 952 panels total (476 each)
system.module_parameters['pdc0'] = 205 #
system.module_parameters['gamma_pdc'] = -0.004 #temperature efficiency loss
system.modules_per_string=68 #476
system.strings_per_inverter=7

#________Create model chain
mc = ModelChain(system,fm.location, aoi_model='physical',name='test')
mc.transposition_model = 'perez'

#________Run the model
weather=forecast_data[['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed']]
mc.run_model(times=weather.index, weather=weather)

#%%

# Utiliza la función read_tmy para cargar el archivo TMY
tmy_data, meta = pvlib.iotools.read_tmy2(archivo_tmy)

# tmy_data es un DataFrame de pandas que contiene los datos meteorológicos
# meta es un diccionario con información sobre el archivo TMY

# Puedes acceder a los datos de manera similar a como lo harías con cualquier DataFrame de pandas
print(tmy_data.head())

# También puedes acceder a la información de metadatos
print(meta)



#%%
# IMPORTANDO DATOS DESDE TMY
archivo = 'DHTMY_E_T6854N.csv'
eltmy = readtmy2(archivo)

#%% CALCULO CON ECUACIONES SOLARES
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
#%%%
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
