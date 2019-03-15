from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from widgets import WorkspaceView, ModalWindow
from settings import appName, appWidth, appHeight, appIcon


class MainWindow(QMainWindow):
	def __init__(self, app):
		super().__init__()
		self.app = app
		self.nodes = {}
		self.resize(appWidth, appHeight)
		self.setWindowTitle(appName)
		self.setWindowIcon(QIcon(appIcon))
		self.setCentralWidget(WorkspaceView(self))
		self.initMenu()
		self.show()

	def initMenu(self):
		self.a_connect = QAction(QIcon('icons/server_go.png'), 'Connect to server...', self)
		self.a_connect.setShortcut('Ctrl+D')
		self.a_connect.triggered.connect(self.showConnectModal)

		self.a_markup = QAction(QIcon('icons/plugin_add.png'), 'Load custom markup...', self)
		self.a_markup.setShortcut('Ctrl+L')
		self.a_markup.triggered.connect(self.showCustomMarkup)

		self.a_sqlquery = QAction(QIcon('icons/script.png'), 'Running SQL Query...', self)
		self.a_sqlquery.setShortcut('Ctrl+R')
		# self.a_sqlquery.setEnabled(False)
		self.a_sqlquery.triggered.connect(self.showSqlModal)

		self.a_quit = QAction(QIcon('icons/cross.png'), 'Quit', self)
		self.a_quit.setShortcut('Ctrl+Q')
		# self.a_quit.setStatusTip('Leave application')
		self.a_quit.triggered.connect(self.app.exit)

		menuBar = self.menuBar()
		m_file = menuBar.addMenu('File')
		m_file.addAction(self.a_connect)
		m_file.addAction(self.a_markup)
		m_file.addAction(self.a_quit)

		toolbar = self.addToolBar('Tools')
		toolbar.addAction(self.a_connect)
		toolbar.addAction(self.a_markup)
		toolbar.addAction(self.a_sqlquery)

	def showConnectModal(self):
		dialog = ModalWindow(self.app.view, self, 'Connection settings', appWidth // 2, appHeight // 2)
		dialog.layout.markup = 'connect.markup'

	def showSqlModal(self):
		dialog = ModalWindow(self.app.view, self, 'Sql Query', appWidth // 2, appHeight // 2)
		dialog.layout.markup = 'sql.markup'

	def showCustomMarkup(self):
		markup_name = QFileDialog.getOpenFileName(self, 'Select markup file', './markups', "Markup (*.markup)")[0]
		dialog = ModalWindow(self.app.view, self, 'Custom Markup', appWidth // 2, appHeight // 2)
		dialog.layout.markup = markup_name

	def addNode(self, key, node):
		self.nodes[key] = node

	def removeNodeById(self, key):
		self.nodes.pop(key, None)

	def handleUpdate(self):
		self.app.handleUpdate()