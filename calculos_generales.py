#programa de calculos generales de sensores-agricolas-LoRaWAN
import numpy as np

#libreria que corrobora las rutas del archivo

import os
import pandas as pd

#comprobar si existe el archivo ademas de eliminar las lineas repetidas 
#con dorp_duplicates
def Archivo(nombre):
    if os.path.isfile(nombre):
        datos = pd.read_csv(nombre, parse_dates = ["timestamp"]).drop_duplicates()
        return datos

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


#filtra el nodo elejido, ademas de que el sort_values permite ordenar 
#de forma cronologica
def filtrar_nodo(datos, id_nodo):
    nodo = datos[datos["nodo"] == id_nodo].sort_values("timestamp")
    return nodo


#calcular las tramas perdidas
def tramas_perdidas(nodo_id):
    #calculamos con la funcion incluida en pandas la diferencia entre cada contador,
    #si al contador del nodo se saltea un conteo este calcula cuantas tramas se salto
    diferencia_tramas_entre_nodos = nodo_id["contador"].diff()
    
    #nos da el valor de cada trama perdida en cada medicion
    perdidas_por_salto = diferencia_tramas_entre_nodos-1
    perdida_total = perdidas_por_salto[perdidas_por_salto > 0].sum()
    
    #cuando el nodo se reinicia y empieza a contar, para esa trama que se perdio 
    #realizamos lo siguiente, evita tramas negativas.
    tramas_perdidas_en_reinicios = nodo_id.loc[diferencia_tramas_entre_nodos<0,
                                               "contador"]
    perdida_total += (tramas_perdidas_en_reinicios[tramas_perdidas_en_reinicios>0].sum())
    return perdida_total


#calcular el promedio de las tramas perdidad
def promedio_tramas_perdidas(nodo_id, tramas_perdidas):
    total_sin_perdidas=len(nodo_id) + tramas_perdidas
    return (tramas_perdidas/total_sin_perdidas)*100.0


#contamos los reincios del nodo
def reinicios_por_nodo(nodo_id):
    #guardamos los valores que sean iguales a cero para saber cuando volvio a 
    #empezar a contar
    contador = nodo_id[nodo_id["contador" ] == 0]

    #le restamos uno para evitar el de inicio
    total_de_reinicios=len(contador)
    return total_de_reinicios-1

#se filtro mediciones corruptas 

def baterias_filtradas(nodo_id):
    return nodo_id.loc[nodo_id["bateria"]!= 0,"bateria"].dropna()

#funcion que permite acceder a las lecturas minimas 

def porcentajes_bajos(lecturas, umbral):
    valores_filtrados=lecturas.dropna()
    cantidad_de_lecturas=len(valores_filtrados)
    total_bajos=(valores_filtrados < umbral).sum()
    return (total_bajos/cantidad_de_lecturas)*100

def lectura_minima(lectura):
    lecturas_validas=lectura.dropna()
    return float(lecturas_validas.min())

