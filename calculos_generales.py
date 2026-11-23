import numpy as np
import matplotlib
import sys 
import os
import pandas as pd


def Archivo(nombre):
    #comprobar si existe el archivo
    if os.path.isfile(nombre):
        datos = pd.read_csv(nombre, parse_dates = ["timestamp"]).drop_duplicates()
        return datos
    else:
        return 
    
#Funcion para obtener la catidad de nodos existentes

def lista_de_Nodos(datos):
    nodos=sorted(datos["nodo"].unique())
    return nodos

#funcion para promediar el RSSI, el mean() promedia sin tomar los nan

def Promedio(columna):
    dbm_mW=10**((columna/10))
    Promedio_en_mW=dbm_mW.mean()
    mW_dbm=10*np.log10(Promedio_en_mW)
    return mW_dbm

#filtra el nodo elejido, ademas de que el sort_values permite ordenar de forma cronologica

def filtrar_nodo(datos,id_nodo):
    nodo=datos[datos["nodo"]==id_nodo].sort_values("timestamp")
    return nodo

def tramas_perdidas(nodo_id):
    #calculamos con la funcion incluida en pandas la diferencia entre cada contador, si al contador del nodo se saltea un conteo este calcula cuantas tramas se salto
    diferencia_tramas_entre_nodos=nodo_id["contador"].diff()
    #nos da el valor de cada trama perdida en cada medicion
    perdidas_por_salto=diferencia_tramas_entre_nodos-1
    perdida_total=perdidas_por_salto[perdidas_por_salto > 0].sum()
    #cuando el nodo se reinicia y empieza a contar, para esa trama que se perdio realizamos lo siguiente.
    tramas_perdidas_en_reinicios=nodo_id.loc[diferencia_tramas_entre_nodos<0, "contador"]
    perdida_total+=(tramas_perdidas_en_reinicios[tramas_perdidas_en_reinicios>0].sum())
    return perdida_total

def promedio_tramas_perdidas(nodo_id,tramas_perdidas):
    total_sin_perdidas=len(nodo_id)+tramas_perdidas
    #condicion en caso de que no existan perdidas
    if total_sin_perdidas > 0:
        porcentaje=(tramas_perdidas/total_sin_perdidas)*100.0
    else:
        porcentaje=0.0
    return porcentaje

def reinicios_por_nodo(nodo_id):
    #guardamos los valores que sean iguales a cero para saber cuando volvio a empezar a contar
    contador=nodo_id[nodo_id["contador" ]== 0]
    #le restamos uno para evitar el de inicio
    total_de_reinicios=len(contador)
    return total_de_reinicios-1

def baterias_bajas(nodo_id, umbral_bateria):
    baterias_sin_ceros=nodo_id.loc[nodo_id["bateria"] != 0,"bateria"]
    baterias_por_bajo_del_umbral=baterias_sin_ceros < umbral_bateria 
    return baterias_por_bajo_del_umbral

def porcentaje_baterias_bajas(nodo_id,baterias_bajas):
    cantidad_de_lecturas=len(nodo_id)
    tota_de_baterias_bajas=baterias_bajas.sum()
    porcentaje=(tota_de_baterias_bajas/cantidad_de_lecturas)*100
    return porcentaje 

def bateria_minima(nodo_id):
    baterias_sin_ceros=nodo_id.loc[nodo_id["bateria"]!= 0,"bateria"]
    if len(baterias_sin_ceros)== 0:
        return 0.0
    return float(baterias_sin_ceros.min())

#funciones para detectar rssi muy bajos
def rssi_minimo(nodo_id):
    if len(nodo_id) == 0:
        return 0.0
    return float(nodo_id["rssi"].min())

def rssi_bajos(nodo_id, umbral_rssi):
    rssi_por_bajo_del_umbral = nodo_id["rssi"] < umbral_rssi
    return rssi_por_bajo_del_umbral

def porcentaje_rssi_bajos(nodo_id, rssi_bajos):
    cantidad_de_lecturas = len(nodo_id)
    if cantidad_de_lecturas == 0:
        return 0.0
    total_de_rssi_bajos = rssi_bajos.sum()
    porcentaje = (total_de_rssi_bajos / cantidad_de_lecturas) * 100
    return porcentaje

