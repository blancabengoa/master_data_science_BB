
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime,timedelta

### Esios

def solicita_datos_general(fecha_ini,fecha_fin,ind):
    headers_={'Accept': 'application/json; application/vnd.esios-api-v1+json',
              'Content-Type': 'application/json',
              'Host': 'api.esios.ree.es',
              'Authorization': 'Token token="9d6bcd627698602fbcd18721cca88b90d0f6e6025963f86be84fa18c87801a10"',
              'Cookie':''
             }
    query_parametros_={'start_date': fecha_ini,
                'end_date':fecha_fin}
    url_='https://api.esios.ree.es/indicators/' + str(ind)
    
    #Hacemos peticion:
    r = requests.get(url_,headers=headers_,params=query_parametros_)
    data=json.loads(r.content)
    df_data=pd.DataFrame(data['indicator']['values'])
    df=pd.DataFrame() 
     df['datetime'] = pd.to_datetime([f[:10] + ' ' + f[11:13] + ':00:00' 
                                     for f in df_data['datetime']],yearfirst=True,format='%Y-%m-%d %H:%M:%S')
    df['value']=df_data['value']
    
    if (ind==475) | (ind==476):
        df=df.groupby('datetime')['value'].sum()
        df=pd.DataFrame(df)
    else:
        df=df.set_index('datetime')
    return df
    
def solicita_datos_precios(fecha_ini,fecha_fin,ind,lista):
   
    headers_={'Accept': 'application/json; application/vnd.esios-api-v1+json',
              'Content-Type': 'application/json',
              'Host': 'api.esios.ree.es',
              'Authorization': 'Token token="9d6bcd627698602fbcd18721cca88b90d0f6e6025963f86be84fa18c87801a10"',
              'Cookie':''
             }
 
    query_parametros_={'start_date': fecha_ini,
                       'end_date': fecha_fin}
    url_='https://api.esios.ree.es/indicators/'+ str(ind)
 
    #Hacemos peticion:
    r = requests.get(url_,headers=headers_,params=query_parametros_)
    data=json.loads(r.content)
    data['indicator']['values']
    df_data=pd.DataFrame(data['indicator']['values'])
    df=pd.DataFrame()
    
    for i in enumerate(lista):
        df_subset=pd.DataFrame()
        df_data_subset=df_data[df_data['geo_id']==i[1][1]]
        df_data_subset.reset_index(drop=True,inplace=True)
        df_subset['datetime']=pd.to_datetime([f[:10] + ' ' + f[11:13] + ':00:00' 
                                              for f in df_data_subset['datetime']],yearfirst=True,format='%Y-%m-%d %H:%M:%S')
        df_subset[str(i[1][0])]=df_data_subset['value']
        df_subset.set_index('datetime',inplace=True)
        df=pd.concat([df,df_subset],axis=1)
    return df 

### Cálculo Reserva D-1

def reserva(lista):
    if (lista[0]<lista[1]) | ((lista[0]==lista[1]) & (lista[2]>lista[1])):
        reserva=0
    else:
        reserva=1 
    return reserva

### Cálculo Weekday considerando Festivos como domingo WD = 7

def WD(elem):
    #Se deben actualizar cada año
    festivos_nac=list(['2019-01-01','2019-05-01','2019-08-15','2019-10-12','2019-12-06','2019-12-25'])
    elem = elem.strftime('%Y-%m-%d')
    
    if elem in festivos_nac:
        WD=7
    else:
        fecha=datetime.strptime(elem,'%Y-%m-%d')
        WD=fecha.weekday()+1
    return WD

### Cálculo columnas asociadas con tiempo

def TEMP(df):
    df['PERIODO']=df['datetime'].dt.hour+1
    df['MES']=df['datetime'].dt.month
    df['WD']=pd.Series(df['datetime'].map(WD)).astype(int)
