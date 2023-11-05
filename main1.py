import os
import sys
import math
import numpy as np
import cv2
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QComboBox, QVBoxLayout
from pydub import AudioSegment
from PIL import Image
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from pyqtgraph import PlotWidget

from gui1 import Ui_MainWindow

class MyMainWindow(QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		super(MyMainWindow, self).__init__(parent)
		QMainWindow.__init__(self, parent)

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.image_file_path = None
		self.audio_file_path = None

		#Instantiating PlotWidget
		self.audio_plot = pg.PlotWidget()
		self.audio_plot.hide()


		#Adding the PlotWidget to the layout
		plot_layout = QVBoxLayout(self.ui.plotWidget)
		plot_layout.addWidget(self.audio_plot)

		#Disabling parameters initially
		self.ui.operationComboBox.show()
		self.ui.audioBrowseButton.hide()
		self.ui.grayScaleButton.hide()
		self.ui.audioAnalysisComboBox.hide()
		self.ui.imageProcessingComboBox.hide()
		self.ui.imagePlotButton.hide()
		self.ui.imageBrowseButton.hide()
		self.ui.basicGroupBox.hide()
		self.ui.interGroupBox.hide()
		self.ui.advancedGroupBox.hide()

		#Connecting UI Signals to slots
		self.ui.operationComboBox.currentIndexChanged.connect(self.appOperations)
		self.ui.audioBrowseButton.clicked.connect(self.select_audio_file)
		self.ui.imageBrowseButton.clicked.connect(self.select_image_file)
		# self.ui.plotWaveformButton.clicked.connect(self.display_audio_waveform)
		self.ui.grayScaleButton.clicked.connect(self.grayScaling)
		self.ui.imageProcessingComboBox.currentIndexChanged.connect(self.operation_level)
		self.ui.brightnessHorizontalSlider.valueChanged.connect(self.update_brightness)




	def appOperations(self):
		selected_operation = self.ui.operationComboBox.currentText()
		if selected_operation == "Audio Processing":
			self.ui.audioBrowseButton.show()
			self.ui.imageDisplay.clear()
			self.audio_plot.hide()
			self.ui.processLabel.setText("<html><font color='white' size='10' face='Arial' style='text-align:center; background-color:blue;'><b>Audio Processing</b></font></html>")
			self.ui.imageBrowseButton.hide()
			self.ui.grayScaleButton.hide()
			self.ui.imageProcessingComboBox.hide()
		elif selected_operation == "Image Processing":
			self.ui.processLabel.clear()
			self.audio_plot.hide()
			self.ui.audioBrowseButton.hide()
			self.ui.imageBrowseButton.show()
			self.ui.processLabel.setText("<html><font color='white' size='10' face='Arial' style='background-color:green; text-align:center'><b>Image Processing</b></font></html>")

	def select_audio_file(self):
		self.audio_plot.hide()
		options = QFileDialog.Options()
		options |= QFileDialog.ReadOnly
		file_path,_ = QFileDialog.getOpenFileName(
			self, "Open Audio File", "", "Audio Files (*.wav *.mp3);;All Files (*)", options=options
		)
		if file_path:
			self.audio_file_path = file_path
			self.ui.processLabel.setText("<html><font color='green' size='6' face='Arial' style= background-color:white;><b>Audio Uploaded Successfully!</b></font></html>")
			self.audio_plot.show()
			self.display_audio_waveform()
	
	def display_image(self, image_data):
	    if isinstance(image_data, str):
	    	image_path = image_data
	        if image_path:
	        	pixmap = QPixmap(image_path)
	        	width = 250
	        	height = 300
	        	pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio)
	            self.ui.imageDisplay.setPixmap(pixmap)
	            self.ui.imageDisplay.setScaledContents(True)
	            self.ui.grayScaleButton.show()
	        else:
	            self.ui.processLabel.setText("No image found!")
	            self.ui.imageDisplay.clear()
	    elif isinstance(image_data, np.ndarray):
	        # If image_data is a NumPy array, display it directly
	        height, width, channel = image_data.shape
	        bytes_per_line = 3 * width
	        image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format_RGB888)
	        pixmap = QPixmap.fromImage(image)
	        self.ui.imageDisplay.setPixmap(pixmap)
	        self.ui.imageDisplay.setScaledContents(True)
	        self.ui.grayScaleButton.show()
	    else:
	        self.ui.processLabel.setText("Invalid image data")
	        self.ui.imageDisplay.clear()

	def select_image_file(self):
		options = QFileDialog.Options()
		options |= QFileDialog.ReadOnly
		file_path, _ = QFileDialog.getOpenFileName(
			self, "Open Image File", "", "Image Files (*.bmp *.jpg *.png);;All Files (*)", options=options
		)
		if file_path:
			self.image_file_path = file_path
			self.display_image(self.image_file_path)
			self.ui.processLabel.setText("<html><font color='green' size='6' face='Arial' style=background-color:white;><b>Image Uploaded Successfully!</b></font></html>")

	def grayScaling(self):
		self.ui.imageDisplay.clear()
		img = cv2.imread(self.image_file_path)
		if img is not None:
			grayScaleImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			height, width = grayScaleImage.shape
			bytes_per_line = 1 * width
			image = QImage(grayScaleImage.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
		
			#Creating a QPixmap and setting it as the QLable's Pixmap
			pixmap = QPixmap.fromImage(image)
			self.ui.imageDisplay.setPixmap(pixmap)
			self.ui.imageDisplay.setScaledContents(True)
			self.ui.imageProcessingComboBox.show()
		else:
			self.ui.processLabel.setText("<html><font color='red' size='6' face='Arial' style=background-color:white;><b>Image Upload Error!!</b></font></html>")
	
	def display_audio_waveform(self):
		self.audio_plot.show()
		if self.audio_file_path:
			audio = AudioSegment.from_file(self.audio_file_path)
			samples = np.array(audio.get_array_of_samples())

			#Creating a time vector based on the sample rate
			sample_rate = audio.frame_rate
			duration = len(samples) / sample_rate
			time_vector = np.linspace(0, duration, len(samples))

			#Creating a PyQtGraph PlotWidget
			plot_widget = self.ui.plotWidget

			#Creating the waveform
			self.audio_plot.plot(time_vector, samples, pen=(0, 0, 255))
			self.audio_plot.setLabel('left', 'Amplitude')
			self.audio_plot.setLabel('bottom', 'Time (s)')
		else:
			self.ui.processLabel.setText("No audio file selected")

	def operation_level(self, index):
		selected_operation = self.ui.imageProcessingComboBox.currentText()
		if selected_operation == "Basic":
			self.ui.interGroupBox.hide()
			self.ui.advancedGroupBox.hide()
			self.ui.basicGroupBox.show()
		elif selected_operation == "Intermediate":
			self.ui.advancedGroupBox.hide()
			self.ui.basicGroupBox.hide()
			self.ui.interGroupBox.show()
		elif selected_operation == "Advanced":
			self.ui.basicGroupBox.hide()
			self.ui.interGroupBox.hide()
			self.ui.advancedGroupBox.show()

	def update_brightness(self):
		brightness = self.ui.brightnessHorizontalSlider.value()
		if self.image_file_path:
			image = cv2.imread(self.image_file_path)
			if image is not None:
				adjusted_image = cv2.convertScaleAbs(image, alpha=brightness/100.0, beta=0)
				self.display_image(adjusted_image)
		else:
			self.ui.processLabel.setText("Error loading Image")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
