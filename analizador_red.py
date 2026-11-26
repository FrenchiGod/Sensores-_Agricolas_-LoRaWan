from calculos_generales import( 
    lista_de_Nodos,
    filtrar_nodo,
    Promedio_de_log_a_lineal,
    promedio_tramas_perdidas,
    tramas_perdidas,
    reinicios_por_nodo,
    porcentajes_bajos,
    lectura_minima,
    baterias_filtradas
)

#estado de los nodos 

def estado_del_nodo(porcentaje_perdidas, porcentaje_baterias, reinicios_por_nodo,Porcentaje_snr,porcentaje_rssi):

    peor_valor = max(porcentaje_baterias,porcentaje_perdidas,Porcentaje_snr,porcentaje_rssi)

    if peor_valor > 7.5 or reinicios_por_nodo >= 2:
        estado = "critico"
    elif peor_valor >= 2.5 or reinicios_por_nodo == 1:
        estado = "alerta"
    else:
        estado = "Normal"

    return estado

#analizar red

def analizar_red(datos,umbral_rssi,umbral_snr,umbral_bateria):
    nodos =lista_de_Nodos(datos)

    #listas que permiten guardar los datos de cada nodo
     
    fila_tabla=[]
    problemas=[]
    lista_perdidas=[]

    for nodo in nodos:
        nodo_datos=filtrar_nodo(datos,nodo)

        #promedios del nodo actual

        rssi_min=lectura_minima(nodo_datos["rssi"])
        snr_min=lectura_minima(nodo_datos["snr"])
        rssi_promedio=Promedio_de_log_a_lineal(nodo_datos["rssi"])
        snr_promedio=Promedio_de_log_a_lineal(nodo_datos["snr"])

        #caidas drasticas de RSSI respecto al umbral
        porcentaje_de_rssi_bajos=porcentajes_bajos(nodo_datos["rssi"], umbral_rssi)

        #bateria minima y porcentaje de la bateria que esta bajo umbral necesario para luego cargar en en el informe cual es el peor problema

        bateria_baja=lectura_minima(baterias_filtradas(nodo_datos))
        porcentaje_de_baterias_bajas_total=porcentajes_bajos(baterias_filtradas(nodo_datos), umbral_bateria)

        #conteo de tramas perdidas y reincios

        perdidas=tramas_perdidas(nodo_datos)
        porcentaje_de_perdidas=promedio_tramas_perdidas(nodo_datos,perdidas)
        reinicios=reinicios_por_nodo(nodo_datos)
        porcentaje_de_rssi_bajos=porcentajes_bajos(nodo_datos["rssi"],umbral_rssi)
        porcentaje_de_srn_bajos=porcentajes_bajos(nodo_datos["snr"],umbral_snr)
        #estado del nodo 

        estado=estado_del_nodo(porcentaje_de_perdidas,porcentaje_de_baterias_bajas_total, reinicios,porcentaje_de_rssi_bajos,porcentaje_de_srn_bajos)

        # Acumular lineas para el informe en texto plano
        if round(bateria_baja, 2) < round(umbral_bateria, 2):
            problemas.append(f"• {nodo}: batería baja ({bateria_baja:.2f} V)")
        if reinicios > 0:
            problemas.append(f"• {nodo}: {reinicios} reinicio")
        if round(rssi_promedio, 2) < round(umbral_rssi, 2):
            problemas.append(f"• {nodo}: RSSI bajo ({rssi_promedio:.0f} dBm)")
        elif round(rssi_min, 2) <= round(umbral_rssi - 5, 2) or porcentaje_de_rssi_bajos > 5.0:
            problemas.append(f"• {nodo}: caída drástica de RSSI ({rssi_min:.1f} dBm)")
        if round(snr_promedio, 2) < round(umbral_snr, 2):
            problemas.append(f"• {nodo}: caida drastica de SNR ({snr_promedio:.1f} dB)")
        elif round(snr_min, 2) <= round(umbral_snr - 5 ,2) or porcentaje_de_srn_bajos > 5.0:
            problemas.append(f"• {nodo}: SNR bajo ({snr_min:.1f}dB)") 
        if perdidas > 0:
            lista_perdidas.append(f"• {nodo}: {perdidas} tramas perdidas ({porcentaje_de_perdidas:.1f}%)")

        datos_fila = [
        str(nodo),
        f"{rssi_promedio:.1f}",
        f"{snr_promedio:.1f}",
        f"{bateria_baja:.2f}",
        f"{porcentaje_de_perdidas:.1f}%",
        estado
        ]
        fila_tabla.append(datos_fila)
        
    #une los elementos de cada lista con un /n para que en el informe se vea uno debajo del otro

    bloque_problemas = "\n".join(problemas) if problemas else "• Sin problemas detectados"
    bloque_perdidas = "\n".join(lista_perdidas) if lista_perdidas else "• Sin pérdida de tramas"

    texto_informe = (
        "Nodos con problemas\n"
        f"{bloque_problemas}\n\n"
        "Pérdida de tramas\n"
        f"{bloque_perdidas}"
    )

    return fila_tabla, texto_informe






