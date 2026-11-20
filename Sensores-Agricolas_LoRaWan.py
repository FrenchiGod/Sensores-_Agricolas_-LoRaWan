import numpy as np
import matplotlib
import sys 
import os
import pandas as pd
os.environ['QT_API']='pyside6'
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FiguresCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from ui_sensores_LoRaWan import Ui_MainWindow

class Sensores_LoRaWan(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()

        #seteo de valores

        self.setupUi(self)

        #self.textEdit_Rssi.setPlainText("-110")
        #self.textEdit_SNR.setPlainText("-5")
        #self.textEdit_bateria.setPlainText("3.3")
        #self.textEdit_ventanaPromedio.setPlainText("6")

        #archivo csv
        
        archivo_csv="nodos.cvs"
        #se corrobora que el archivo exista
        if os.path.isfile(archivo_csv):
            self.df=pd.read_csv(archivo_csv, parse_dates=["timestamp"])
            nodos=sorted(self.df["nodo"].unique())

            #auto llenado del listado de nodos

            self.comboBox_Nodos.clear()
            for nodo in nodos:
                self.comboBox_Nodos.addItem(str(nodo))
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
        self.Analizar()

    def Analizar(self):
        #corroborar si existe el archivo
        if self.df is None:
            return
        #accede a los elementos de la lista
        nodo_lista=self.comboBox_Nodos.currentText()
        try: 
            umbral_Rssi=float(self.textEdit_Rssi.toPlainText())
        except ValueError:
            umbral_Rssi=-110



 # Inicializar el administrador de la aplicación Qt pasándole los argumentos del sistema
app = QApplication(sys.argv)
# Crear una instancia de la ventana principal
window = Sensores_LoRaWan()
# Mostrar la ventana en pantalla
window.show()
# Iniciar el bucle de eventos y asegurar un cierre limpio del proceso
sys.exit(app.exec())


        

    
                