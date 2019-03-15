import sys
import logging
from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QDockWidget
from PyQt5.QtCore import Qt
from controller import MainWindow
from models import DataModel
from settings import appMarkup


class Application(QApplication):
	def __init__(self, *args):
		super().__init__(*args)
		self.controller = MainWindow(self)
		# self.initLogging()
		self.model = DataModel(self, "QPSQL")
		# self.model.openConnection('hospital', 'abel')
		self.markup = appMarkup

	@property
	def view(self):
		return self.controller.centralWidget()

	@property
	def markup(self):
		return self.view.markup

	@markup.setter
	def markup(self, value):
		self.view.markup = value

	def handleUpdate(self):
		self.view.handleUpdate()
		self.model.notifyWatchers()

	def initLogging(self):
		self.logger = QDockWidget('Logging console', self.controller)
		self.logger.setAllowedAreas(Qt.BottomDockWidgetArea)
		self.logger.setWidget(QPlainTextEdit())
		self.controller.addDockWidget(Qt.BottomDockWidgetArea, self.logger)

		# logging.basicConfig(filename='log.txt', level=logging.INFO)
		logging.basicConfig(level=logging.INFO)
		logging.info('Application started')

		sys.excepthook = self.exception_handler

	def log(self, text):
		self.logger.widget().appendPlainText(text)

	def exception_handler(self, type, value, tb=None):
		self.log(str(value))
		# logging.exception(str(value))
