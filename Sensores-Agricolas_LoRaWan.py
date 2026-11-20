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
from ui_sensores_LoRaWan import Ui_MainWindow

class Sensores_LoRaWan(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        #seteo de valores

        self.setupUi(self)
        self.textEdit_Rssi.setPlainText("-110")
        self.textEdit_SNR.setPlainText("-5")
        self.textEdit_bateria.setPlainText("3.3")
        self.textEdit_ventanaPromedio.setPlainText("6")

        #grafica Rssi

        self.figure_Rssi=Figure(facecolor='#FFFFFF')
        self.canvas_Rssi=FiguresCanvas(self.figure_Rssi)
        self.ax=self.figure_Rssi.add_subplot(111)

        layout_1=QVBoxLayout(self.widget_Rssi)
        layout_1.self.setContentsMargins(0, 0, 0, 0)
        layout_1.addWidget(self.canvas_Rssi)

        #grafica Bateria

        self.figure_bateria=Figure(facecolor='#FFFFFF')
        self.canvas_bateria=FiguresCanvas(self.figure_bateria)
        self.ax=self.figure_bateria.add_subplot(111)

        layout_1=QVBoxLayout(self.widget_bateria)
        layout_1.self.setContentsMargins(0, 0, 0, 0)
        layout_1.addWidget(self.canvas_bateria)

        self.pushButton_Actualizar.clicked.connect(self.actualizar_grafico)
        self.actualizar_grafico()
    
                