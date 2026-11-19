import numpy as np
import matplotlib
import sys 
import os
os.environ['QT_API']='pyside6'
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FiguresCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from ui_sensores_LoRaWan import Ui_MainWindow

class Sensores_LoRaWan(QMainWindow, Ui_MainWindow):
    
