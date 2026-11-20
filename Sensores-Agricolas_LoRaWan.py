import numpy as np
import matplotlib
import sys 
import os
import pandas as pd
os.environ['QT_API']='pyside6'
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FiguresCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PySide6.QtCore import QSize

#importamos la interfaz grafica
from ui_sensores_LoRaWan import Ui_MainWindow

from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QColor

#importamos para graficar 

import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter


class Sensores_LoRaWan(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()

        #seteo de valores

        self.setupUi(self)


        #archivo csv
        
        archivo_csv="nodos.csv"
        if os.path.isfile(archivo_csv):
            self.df = pd.read_csv(archivo_csv, parse_dates=["timestamp"]).drop_duplicates()
            nodos = sorted(self.df["nodo"].unique())

            #auto llenado del listado de nodos

            self.comboBox.clear()
            for nodo in nodos:
                self.comboBox.addItem(str(nodo))

        else:
            self.df=None
            #QMessageBox.critical(self, "error", "archivo csv inexistente")

        #grafica Rssi

        self.figure_Rssi=Figure(facecolor='#FFFFFF')
        self.canvas_Rssi=FiguresCanvas(self.figure_Rssi)
        self.ax_Rssi=self.figure_Rssi.add_subplot(111)

        layout_1=QVBoxLayout(self.frame_Rssi)
        layout_1.setContentsMargins(0, 0, 0, 0)
        layout_1.addWidget(NavigationToolbar2QT(self.canvas_Rssi, self))
        layout_1.addWidget(self.canvas_Rssi)

        #grafica Bateria

        self.figure_bateria=Figure(facecolor='#FFFFFF')
        self.canvas_bateria=FiguresCanvas(self.figure_bateria)
        self.ax_bateria=self.figure_bateria.add_subplot(111)

        layout_2=QVBoxLayout(self.frame_Bateria)
        layout_2.setContentsMargins(0, 0, 0, 0)
        layout_2.addWidget(NavigationToolbar2QT(self.canvas_bateria, self))
        layout_2.addWidget(self.canvas_bateria)

        self.pushButton.clicked.connect(self.Analizar)
        self.comboBox.currentTextChanged.connect(self.Analizar)
        self.Analizar()

        #modificacion de la barra de herramientas del grafico


    def Analizar(self):

        #corroborar si existe el archivo

        if self.df is None:
            return
        
        #accede a los elementos

        nodo_lista=self.comboBox.currentText()
        umbral_rssi=self.RSSI.value()
        umbral_bateria=self.Bateria.value()
        umbral_snr=self.SNR.value()
        df_sin_Reinicios=self.df.drop_duplicates().copy()

        #informe

        nodos=sorted(self.df["nodo"].unique())
        self.tableWidget.setRowCount(len(nodos))

        #por cada nodo guardamos su valor y calculamos su promedio en SRN y RSSI ademas de su bateria minima y los saltos del contador

        for fila, nodo in enumerate(nodos):

            #datos de cada nodo en el tiempo 
            df_nodo=df_sin_Reinicios[df_sin_Reinicios["nodo"]==nodo].sort_values("timestamp").copy()
            #promedios
            rssi_promedio=10 * np.log10((10 ** (df_nodo["rssi"] / 10)).mean())
            snr_promedio= 10 * np.log10((10 ** (df_nodo["snr"] / 10)).mean())
            #filtramos las baterias con valores nulos
            baterias_con_valor=df_nodo[df_nodo["bateria"]> 0 ]["bateria"]
            bateria_minino=baterias_con_valor.min()
            #conteo de tramas perdidas y reinicios reales 
            differencia_contador=df_nodo["contador"].diff()
            reinicios=int((differencia_contador < 0).sum())
            saltos=differencia_contador[differencia_contador > 1]
            perdidas= int ((saltos-1).sum())
            #despues del reinicio 
            arranques_despues_del_reinicio =df_nodo.loc[differencia_contador < 0 , "contador"]
            perdidas += int(arranques_despues_del_reinicio[arranques_despues_del_reinicio > 0].sum())
            #calculo del porcentaje de perdidas
            total_sin_perdidas=len(df_nodo)+perdidas
            porcentaje_perdidas=(perdidas/total_sin_perdidas*100.0)if total_sin_perdidas > 0 else 0.0
            #estado
            if bateria_minino < umbral_bateria or rssi_promedio < umbral_rssi or porcentaje_perdidas > 10.0:
                estado = "critico"
                bg = QColor("#f8d7da")
                fg = QColor("#842029")
            elif snr_promedio < umbral_snr or reinicios > 0 or porcentaje_perdidas > 3.0:
                estado= "alerta"
                bg= QColor("#fff3cd")
                fg= QColor("#664d03")
            else:
                estado ="Normal"
                bg= QColor("#d1e7dd")
                fg= QColor("#0f5132")
            #insertamos datos en la tabla
            datos_fila = [
                str(nodo),
                f"{rssi_promedio:.1f}",
                f"{snr_promedio:.1f}",
                f"{bateria_minino:.2f}",
                f"{porcentaje_perdidas:.1f}%",
                estado
            ]
            for col, texto in enumerate(datos_fila):
                item = QTableWidgetItem(texto)
                if col == 5:
                    item.setBackground(bg)
                    item.setForeground(fg)
                self.tableWidget.setItem(fila, col, item)
        
        self.tableWidget.resizeColumnsToContents()

        #Graficas
        
        Ventana=self.ventana.value()

        #cargamos los datos del nodo elejido a graficar

        df_grafico=self.df[self.df["nodo"]==nodo_lista].sort_values("timestamp").copy()

        if df_grafico.empty:
            return
        
        #agrupamos los valores por hora para que no sea cada 10 min

        fin = df_grafico["timestamp"].max()
        inicio = fin.floor("D") - pd.Timedelta(days=6)
        df_grafico = df_grafico[df_grafico["timestamp"] >= inicio].copy()

        # agrupamos por hora (pasando RSSI a mW para promediar bien)

        df_grafico.loc[df_grafico["bateria"] == 0, "bateria"] = np.nan
        df_grafico["rssi_mw"] = 10 ** (df_grafico["rssi"] / 10)
        df_grafico = df_grafico.set_index("timestamp")[["rssi_mw", "bateria"]].resample("1h").mean().reset_index()
        df_grafico["rssi"] = 10 * np.log10(df_grafico["rssi_mw"])

        # promedio movil del ventana

        promedio_movil_mw = df_grafico["rssi_mw"].rolling(window=Ventana, min_periods=1).mean()
        df_grafico["rssi_movil"] = 10 * np.log10(promedio_movil_mw)

        #filtramos las baterias que no sean cero
        df_bateria = df_grafico[df_grafico["bateria"] > 0]

        #limpiamos los ejes para que cuando se actualice cambie
        self.ax_Rssi.clear()
        self.ax_bateria.clear()

        # etiquetas para los dias en el eje x
        dias_ejex = {0: "lun", 1: "mar", 2: "mier", 3: "jue", 4: "vie", 5: "sab", 6: "dom"}
        fechas_dias = pd.date_range(start=df_grafico["timestamp"].min().floor("D"), periods=7, freq="1D")
        etiquetas_dias = []
        for dia in fechas_dias:
            etiquetas_dias.append(dias_ejex[dia.weekday()])

        # grafico del Rssi
        self.ax_Rssi.plot(df_grafico["timestamp"], df_grafico["rssi"], color="#6baed6", linewidth=1.0, label="RSSI")
        self.ax_Rssi.plot(df_grafico["timestamp"], df_grafico["rssi_movil"], color="orange", linewidth=2.0, label="Promedio móvil")
        self.ax_Rssi.axhline(y=umbral_rssi, color="red", linestyle="--", linewidth=1.5, label="Umbral")

        self.ax_Rssi.set_title(f"RSSI del nodo {nodo_lista} (dBm)", fontsize=10, fontweight="bold")
        self.ax_Rssi.set_ylabel("RSSI (dBm)")
        self.ax_Rssi.set_ylim(-125, -80)
        self.ax_Rssi.set_yticks([-125, -110, -95, -80])
        self.ax_Rssi.set_xlim(df_grafico["timestamp"].min(), df_grafico["timestamp"].max())
        self.ax_Rssi.set_xticks(fechas_dias)
        self.ax_Rssi.set_xticklabels(etiquetas_dias)
        self.ax_Rssi.grid(True, linestyle="--", alpha=0.4, color="gray")
        self.ax_Rssi.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, fontsize=8)

        # grafica de la bateria 

        self.ax_bateria.plot(df_bateria["timestamp"], df_bateria["bateria"], color="green", linewidth=1.8, label="Batería")
        self.ax_bateria.axhline(y=umbral_bateria, color="red", linestyle="--", linewidth=1.5, label="Umbral")

        self.ax_bateria.set_title(f"Tensión de batería del nodo {nodo_lista} (V)", fontsize=10, fontweight="bold")
        self.ax_bateria.set_ylabel("Batería (V)")
        self.ax_bateria.set_ylim(2.8, 3.8)
        self.ax_bateria.set_yticks([2.8, 3.3, 3.8])
        self.ax_bateria.set_xlim(df_bateria["timestamp"].min(), df_bateria["timestamp"].max())
        self.ax_bateria.set_xticks(fechas_dias)
        self.ax_bateria.set_xticklabels(etiquetas_dias)
        self.ax_bateria.grid(True, linestyle="--", alpha=0.4, color="gray")
        self.ax_bateria.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=8)

        #se ajusto los margenes (left=0.13 para que se lea "RSSI (dBm)" y bottom=0.30 para la leyenda)

        self.figure_Rssi.subplots_adjust(left=0.13, right=0.98, top=0.85, bottom=0.30)
        self.canvas_Rssi.draw()

        self.figure_bateria.subplots_adjust(left=0.13, right=0.98, top=0.85, bottom=0.30)
        self.canvas_bateria.draw()

 # Inicializar el administrador de la aplicación Qt pasándole los argumentos del sistema
app = QApplication(sys.argv)
# Crear una instancia de la ventana principal
window = Sensores_LoRaWan()
# Mostrar la ventana en pantalla
window.show()
# Iniciar el bucle de eventos y asegurar un cierre limpio del proceso
sys.exit(app.exec())


        

    
                