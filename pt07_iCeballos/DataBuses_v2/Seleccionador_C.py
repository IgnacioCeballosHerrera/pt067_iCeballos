# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 11:09:15 2023

@author: MECLab-03
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
# import geopandas as gpd
import mpu
from os import listdir

#%%
def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

folders=['C_abril_2020','C_agosto_2019','C_diciembre_2019','C_enero_2020','C_febrero_2020',\
         'C_junio_2020','C_noviembre_2019','C_octubre_2019','C_septiembre_2019',\
             'C_agosto_2020','C_julio_2020','C_marzo_2020','C_mayo_2020']
    

dictionary={}
for i in folders:
    filenames = find_csv_filenames(i)
    dictionary[i]= filenames


folder=folders[1] #
patente= dictionary[folder][5]
print('Final '+str(len(dictionary[folder])-1))
df=pd.read_csv(folder+'/'+patente)

#%%
h=pd.to_datetime(df['hora'])
deltat=h.copy()
Deltatime=np.zeros([len(deltat)])
# Num_Travel=np.ones([len(deltat)])*-1
# travel=0
extremos=[0]
largo=[]
for i in range(len(h)):
    if i==0:
        deltat[i]=h[i]-h[i]
    else:
        deltat[i]=h[i]-h[i-1]
    Deltatime[i]=deltat[i].total_seconds()
    if Deltatime[i]>600:
        # travel+=1
        extremos.append(i)
        largo.append(extremos[-1]-extremos[-2])
    # Num_Travel[i]=int(travel)
extremos.append(i)
largo.append(extremos[-1]-extremos[-2])
df['deltaTime']=Deltatime

indices=[]
for i in range(len(largo)):
    if largo[i]<10:
        indices=indices+list(range(extremos[i],extremos[i+1]))

df2=df.drop(indices).reset_index().drop(columns='index')
#%%

travel=0
travel_list=[0]
extremos=[0]
largo=[]
for i in range(len(df2)):
    if df2['deltaTime'][i]>600:
        travel+=1
        travel_list.append(travel)
        extremos.append(i)
        largo.append(extremos[-1]-extremos[-2])
extremos.append(i)
largo.append(extremos[-1]-extremos[-2])


#%%
def onclick(event):
    global flag
    if  event.button == 1:
        flag=True
        print('click izquierdo '+str(flag))
        
        plt.close()
    elif event.button == 3:
        flag=False
        print('click derecho '+str(flag))
        plt.close()


fig, ax = plt.subplots()
ax.plot(np.random.rand(10))
cid = fig.canvas.mpl_connect('button_press_event', onclick)
# print(flag)
#%%
i=0
aceptado=np.zeros(len(travel_list))
dfCompleto=pd.read_csv('GroundTruth.csv')
#%%
fig, ax = plt.subplots()
if i < len(travel_list):
    latitud, longitud = np.array(df2['latitud'][extremos[i]:extremos[i+1]]), np.array(df2['longitud'][extremos[i]:extremos[i+1]])
    ax.plot(dfCompleto['latitude'],dfCompleto['longitude'],'r')
    ax.plot(latitud, longitud,'b')
else:
    ax.plot(np.random.rand(10))
cid = fig.canvas.mpl_connect('button_press_event', onclick)
if i > 0:
    aceptado[i-1]=flag
i+=1
print(flag)

#%%
indices=[]
for i in range(len(aceptado)):
    if not bool(aceptado[i]):
        indices=indices+list(range(extremos[i],extremos[i+1]))
df2=df2.drop(indices).reset_index().drop(columns='index')
#%%
h=pd.to_datetime(df2['hora'])
deltat=h.copy()
Deltatime=np.zeros([len(deltat)])

travel=0
travel_list=[0]
extremos=[0]
largo=[]
Num_Travel=np.ones([len(df2)])*-1
for i in range(len(df2)):
    if i==0:
        deltat[i]=h[i]-h[i]
    else:
        deltat[i]=h[i]-h[i-1]
    Deltatime[i]=deltat[i].total_seconds()
    if Deltatime[i]>600:
        travel+=1
        travel_list.append(travel)
        extremos.append(i)
        largo.append(extremos[-1]-extremos[-2])
    Num_Travel[i]=travel
extremos.append(i)
largo.append(extremos[-1]-extremos[-2])
df2['deltaTime']=Deltatime
df2['travel']=np.int8(Num_Travel)
for i in range(len(travel_list)):
    plt.plot(df2['latitud'][extremos[i]:extremos[i+1]], np.array(df2['longitud'][extremos[i]:extremos[i+1]]))

df2=df2.drop(len(df2['travel'])-1)
#%%
df2.to_csv(folder+'_v2/'+patente)