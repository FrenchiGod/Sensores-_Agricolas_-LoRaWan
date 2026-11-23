from calculos_generales import( 
    lista_de_Nodos,
    filtrar_nodo,
    Promedio,
    promedio_tramas_perdidas,
    tramas_perdidas,
    reinicios_por_nodo,
    baterias_bajas,
    porcentaje_baterias_bajas,
    bateria_minima,
    rssi_minimo,
    rssi_bajos,
    porcentaje_rssi_bajos
)


#estado de los nodos 
def estado_del_nodo(porcentaje_perdidas, porcentaje_baterias, 
                    porcentaje_reinicios):
    problemas_nodo = {
        "Tramas perdidas": porcentaje_perdidas,
        "Batería baja": porcentaje_baterias,
        "Reinicios": porcentaje_reinicios
    }
    peor_problema = max(problemas_nodo, key = problemas_nodo.get)
    peor_valor = problemas_nodo[peor_problema]

    if peor_valor < 2.5:
        estado = "Normal"
        peor_problema = "Ninguno"
    elif peor_valor <= 7.5:
        estado = "alerta"
    else:
        estado = "critico"

    return estado, peor_problema, peor_valor


#analizar red
def analizar_red(datos, umbral_rssi, umbral_snr, umbral_bateria):
    nodos = lista_de_Nodos(datos)

    #listas que permiten guardar los datos de cada nodo     
    fila_tabla = []
    problemas = []
    lista_perdidas = []
    for nodo in nodos:
        nodo_datos = filtrar_nodo(datos, nodo)

        #promedios del nodo actual
        rssi_promedio = Promedio(nodo_datos["rssi"])
        snr_promedio = Promedio(nodo_datos["snr"])

        #caidas drasticas de RSSI respecto al umbral
        rssi_min = rssi_minimo(nodo_datos)
        cantidad_rssi_bajos = rssi_bajos(nodo_datos, umbral_rssi)
        porcentaje_de_rssi_bajos = porcentaje_rssi_bajos(nodo_datos,
                                                         cantidad_rssi_bajos)

        #bateria minima y porcentaje de la bateria que esta bajo umbral
        bateria_baja = bateria_minima(nodo_datos)
        cantidad_baterias_bajas = baterias_bajas(nodo_datos, umbral_bateria)
        porcentaje_de_baterias_bajas_total = porcentaje_baterias_bajas(nodo_datos,
                                                                       cantidad_baterias_bajas)

        #conteo de tramas perdidas y reincios
        perdidas = tramas_perdidas(nodo_datos)
        porcentaje_de_perdidas = promedio_tramas_perdidas(nodo_datos,perdidas)
        reinicios = reinicios_por_nodo(nodo_datos)

        #estado del nodo y cual es su peor caso o error importante
        estado, peor_problema , peor_valor=estado_del_nodo(porcentaje_de_perdidas,
                                                           porcentaje_de_baterias_bajas_total, reinicios)

        # Acumular lineas para el informe en texto plano
        if round(bateria_baja, 2) < round(umbral_bateria, 2):
            problemas.append(f"• {nodo}: batería baja ({bateria_baja:.2f} V)")
        if round(reinicios, 2) > 0:
            problemas.append(f"• {nodo}: {reinicios} reinicio")
        if round(rssi_promedio, 2) < round(umbral_rssi, 2):
            problemas.append(f"• {nodo}: RSSI bajo ({rssi_promedio:.0f} dBm)")
        elif round(rssi_min, 2) <= round(umbral_rssi - 5, 2) or porcentaje_de_rssi_bajos > 5.0:
            problemas.append(f"• {nodo}: caída drástica de RSSI ({rssi_min:.1f} dBm)")
        if round(snr_promedio, 2) < round(umbral_snr, 2):
            problemas.append(f"• {nodo}: SNR bajo ({snr_promedio:.1f} dB)")

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

    if problemas:
        bloque_problemas = "\n".join(problemas)
    else:
        bloque_problemas = "• Sin problemas detectados"

    if lista_perdidas:
        bloque_perdidas = "\n".join(lista_perdidas)
    else:
        bloque_perdidas = "• Sin pérdida de tramas"

    texto_informe = (
        "Nodos con problemas\n"
        f"{bloque_problemas}\n\n"
        "Pérdida de tramas\n"
        f"{bloque_perdidas}"
    )

    return fila_tabla, texto_informe






