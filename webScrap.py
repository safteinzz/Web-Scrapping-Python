# -*- coding: utf-8 -*-
"""
https://github.com/safteinzz/Web-Scrapping-Python

@author: SaFteiNZz
"""
# =============================================================================
#         ~DOC
#
#            https://github.com/kiengiv/TripAdvisorPython/blob/master/Script_Hotel
#            https://www.dataquest.io/blog/web-scraping-tutorial-python/
#            https://realpython.com/python-requests/
#            https://www.crummy.com/software/BeautifulSoup/bs4/doc/
#            https://www.youtube.com/watch?v=-qYljhR4hsc
#            https://textblob.readthedocs.io/en/dev/quickstart.html
#            https://stackabuse.com/python-for-nlp-tokenization-stemming-and-lemmatization-with-spacy-library/
#            https://spacy.io/universe/project/spacy-textblob
#            https://spacy.io/api/token
#
# =============================================================================
#         ~CONSTANTES
# =============================================================================

ICOENLACE = 'resources/safteinzz.ico'
GUIENLACE = 'resources/interfazWebScrap.ui'

# =============================================================================
#         ~IMPORTS
# =============================================================================
#Relacionado con el scrapping
import requests, re
from bs4 import BeautifulSoup
#from urllib.parse import urljoin, urlparse
#from lxml import html

#Prediccion
from textblob import TextBlob, Word
import spacy
sp = spacy.load('en_core_web_sm')
from resources.unicodetoascii import unicodetoascii

#Datasets y models
from resources.pandasmodel import PandasModel
import pandas as pd

#Almacenamiento
import csv

# --- Interfaz
#Lanzamiento
import sys
#Ventana
from PyQt5 import uic
#Messagebox
import ctypes
#PyQT5
from PyQt5 import QtGui
#Widgets pyQT5
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication
#Importar interfaz
Ui_MainWindow, QtBaseClass = uic.loadUiType(GUIENLACE)

# =============================================================================
#         ~FUNCIONES PUBLICAS
# =============================================================================
# ~Funcion alertas messagebox
#
#            @text comentario del messagebox
#            @title titulo ventana messagebox
#            @style (INT) tipo de ventana
#                  0 : OK
#                  1 : OK | Cancel
#                  2 : Abort | Retry | Ignore
#                  3 : Yes | No | Cancel
#                  4 : Yes | No
#                  5 : Retry | No 
#                  6 : Cancel | Try Again | Continue
#            
# =============================================================================
def Messagebox(text, title, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)    

# =============================================================================
# ~Seleccionar Ruta de fichero/carpeta   
#
#    @filtro => Sera el tipo de extension
#    @titulo  => Titulo de la ventana
#    @guardar => Booleano para saber si se quiere cargar o guardar
#    - 1 = guardar
#    - 0 = cargar
#    @carpetas => Booleano para saber si se quiere carpetas o archivos
#    - 1 = carpetas
#    - 0 = ficheros
#    Ejemplo filtro: "xls(*.xls);;csv(*.csv)"  
#
# ============================================================================= 
def seleccionarFichero(filtro, titulo, guardar, carpetas):
    qFD = QFileDialog()
    if carpetas == 1:
        return QFileDialog.getExistingDirectory(qFD, titulo, "", QFileDialog.ShowDirsOnly)
    else:        
        if guardar == 0:                   
            return QFileDialog.getOpenFileName(qFD, titulo, "",filtro)
        elif guardar == 1:
            return QFileDialog.getSaveFileName(qFD, titulo, "",filtro)
        
     

# -----------------------------------------------------------------------------
# ~Clase ventana
# =============================================================================
class mainClass(QMainWindow):
    
    def __init__(self):
        super(mainClass, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 
        self.setWindowIcon(QtGui.QIcon(ICOENLACE))
        
# 
#         ~Eventos links
# =============================================================================
        
# ---------- Botones
        #Boton seleccionar CSV
        self.ui.pBArchivoBuscar.clicked.connect(self.pBArchivoBuscarClicked)   
        #Boton analizar CSV
        self.ui.pBAnalizar.clicked.connect(self.pBAnalizarClicked)   
        #Botton scrappear web
        self.ui.pBDescargar.clicked.connect(self.pBDescargarClicked)   
        
# ---------- Otros
        #Line edit URL
        self.ui.tEURLPagina.mousePressEvent = self.tEURLPaginaClicked


# 
# ~Funciones eventos
# =============================================================================
#     ~Evento clickar textedit tEURLPagina 
# =============================================================================
    def tEURLPaginaClicked(self, event):
        self.ui.tEURLPagina.setText('')
        self.ui.tEURLPagina.setTextColor(QtGui.QColor(0,0,0))
    
# =============================================================================
#     ~Evento descargar pagina en CSV
# =============================================================================
    def pBDescargarClicked( self ):
#        Comprobar que ha rellenado la URL
        url = self.ui.tEURLPagina.toPlainText()
        if not url:
            Messagebox('Debes introducir una URL', 'Error', 1)        
            return  
        
#        Seleccionar fichero
        rutaFichero = seleccionarFichero("csv(*.csv)", "Seleccionar donde guardar fichero", 1, 0)
        if not rutaFichero[0]:
            Messagebox('Debes seleccionar donde guardar el fichero', 'Error', 1)        
            return
        
#        Extraer pagina y comprobar
        res = requests.get(self.ui.tEURLPagina.toPlainText())
        if not res:
            Messagebox('Error en la carga de la pagina', 'Error', 1) 
            return
            
        else:
#            Extraer contenido de la pagina
            soup = BeautifulSoup(res.content, 'html.parser')
            comentarios = soup.find_all('p',{'class': 'partial_entry'},text=re.compile('(.*?)',re.UNICODE))
            
#            Crear y meter datos en csv
            cantidadComent = 0
            with open(rutaFichero[0], 'w', newline='') as f:
                fieldnames = ['comentario']
                thewriter = csv.DictWriter(f, fieldnames=fieldnames)
                
                for com in comentarios:
                    com = str(com.encode(encoding='UTF-8',errors='strict'))
                    x = re.search(">(.*?)<", com) #esta expresion regular directamente en la linea 170 no funciona
                    res = x.group(1)
                    res = unicodetoascii(res)
                    thewriter.writerow({'comentario' : res})
                    cantidadComent += 1
                  
#                Sacar resultados en el plain text edit
                log = str(cantidadComent) + " filas de comentarios almacenados en " + rutaFichero[0]
                self.ui.pTEStatus.appendPlainText(log)
        
# =============================================================================
#     ~Evento seleccionar CSV para analisis  
# =============================================================================
    def pBArchivoBuscarClicked( self ):
        rutaFichero = seleccionarFichero("csv(*.csv)", "Seleccionar fichero para analisis", 0, 0)
        if not rutaFichero[0]:
            Messagebox('Debes seleccionar un fichero para analisis', 'Error', 1)        
            return
        
        self.ui.lEArchivo.setText(rutaFichero[0])
        
# =============================================================================
#     ~Evento analizar CSV
# =============================================================================
    def pBAnalizarClicked( self ):
#        Checkear si el campo no esta rellenado
        archivo = self.ui.lEArchivo.text()
        if not archivo:
            Messagebox('Debes Seleccionar un fichero', 'Error', 1)        
            return 
        
        with open(archivo) as f:
            reader = csv.reader(f)
            rows = []
            valoraciones = []            
            for row in reader:  
                frase = sp(row[0]) #Tokenización
                nuevaFrase = ''
                for word in frase:
                    if word.is_stop: continue #quitar stopwords
                    if word.like_url: #standarizar urls
                        w = "url"
                    elif word.like_email: #standarizar mails
                        w = "email"                    
                    else:
                        w = Word(Word(str(word)).spellcheck()[0][0]) #Correción (coje el mayor porcentaje)
                        w = sp(str(w))[0].lemma_ #Lematización                        
                    nuevaFrase += w + " "
                    
                t = TextBlob(nuevaFrase)
                rows.append(row[0])
                sentimiento = t.sentiment
                if -0.20 < sentimiento.polarity < 0.20:
                    valoraciones.append('Neutro')
                elif sentimiento.polarity <= -0.20:
                    valoraciones.append('Negativo')                    
                elif sentimiento.polarity >= 0.20:
                    valoraciones.append('Positivo')

        diccionario = {'Comentario': rows, 'Valoracion': valoraciones}  
        df = pd.DataFrame(diccionario) 
        modelo = PandasModel(df)
        self.ui.tVResultado.setModel(modelo)
        self.ui.tVResultado.setColumnWidth(0, 520)
        self.ui.tVResultado.horizontalHeader().setStretchLastSection(True)        
# 
# RUNUP
# =============================================================================
# Función MAIN
###############################################################################
def main():
    app = QApplication(sys.argv)
    window = mainClass()
    window.show()
    app.exec_()
# Ejecucion -------------------------------------------------------------------
if __name__ == '__main__':
    main()   
#------------------------------------------------------------------------------
    