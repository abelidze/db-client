import json
import os.path
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLineEdit, QPlainTextEdit, QPushButton, QLabel,
		QGroupBox, QTabWidget, QTableView, QTreeWidget, QTreeWidgetItem, QDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from helpers import MappingList


###################
## Nodes and co. ##
###################

class BaseNode(QWidget):
	def __init__(self, window, layout=None, data=None, node_type=1):
		super().__init__()
		self.window = window
		self.layout = layout
		self.process_data(data)
		if layout is not None:
			if node_type == 1:
				self.setMaximumSize(QSize(self.width, self.height))
				layout.addWidget(self, self.y, self.x, self.row, self.col)
			elif node_type == 2:
				layout.addLayout(self, self.y, self.x, self.row, self.col)

	def process_data(self, data):
		if data is None: return

		if 'x' in data: self.x = data['x']
		else: self.x = 0
		if 'y' in data: self.y = data['y']
		else: self.y = 0
		if 'c' in data: self.col = data['c']
		else: self.col = 1
		if 'r' in data: self.row = data['r']
		else: self.row = 1
		if 'w' in data: self.width = data['w']
		else: self.width = 1920
		if 'h' in data: self.height = data['h']
		else: self.height = 1920

	def handleUpdate(self, *args):
		pass


class Layout(QGridLayout, BaseNode):
	def __init__(self, window, parent, data=None, node_type=2, *args):
		layout = []
		if node_type == 0:
			layout = [parent]
		# super().__init__(*layout)
		QGridLayout.__init__(self, *layout)
		BaseNode.__init__(self, window, parent, data, node_type, *args)
		self.__markup = 'undefined'

	@property
	def markup(self):
		return self.__markup

	@markup.setter
	def markup(self, value):
		if not os.path.isfile(value):
			value = './markups/{}'.format(value)

		try:
			value = json.load(open(value, 'r'))
		except FileNotFoundError:
			raise Exception("Markup doesn't exists: {0}".format(value))
		except ValueError:
			raise Exception("Wrong markup-format: {0}".format(value))

		if 'title' in value:
			self.layout.setWindowTitle('{}'.format(value['title']))

		if 'nodes' in value and isinstance(value['nodes'], list):
			for node in value['nodes']:
				self.window.addNode(node['id'], generateNode(node['type'], self.window, self, node['data']))
		self.__markup = value

	def process_data(self, data):
		if data is None: return

		BaseNode.process_data(self, data)
		if 'markup' in data:
			self.markup = data['markup']


class Button(QPushButton, BaseNode):
	def __init__(self, *args):
		super(QPushButton, self).__init__()
		BaseNode.__init__(self, *args)

	def process_data(self, data):
		BaseNode.process_data(self, data)
		if 'caption' in data:
			self.setText(data['caption'])
		self.source = []
		if 'source' in data:
			self.source = data['source']
		if 'onclick' in data:
			pass
			# self.clicked.connect(partial(processAction[data['onclick']], self.source))


class InputField(QLineEdit, BaseNode):
	def __init__(self, *args):
		super(QLineEdit, self).__init__()
		BaseNode.__init__(self, *args)
		try: self.label
		except: self.label = None

	def process_data(self, data):
		BaseNode.process_data(self, data)
		if 'caption' in data:
			self.label = QLabel(data['caption'])
			self.label.setAlignment(Qt.AlignRight)
			self.layout.addWidget(self.label, self.y, self.x)
			self.x += 1


class TextArea(QPlainTextEdit, BaseNode):
	def __init__(self, *args):
		super(QPlainTextEdit, self).__init__()
		BaseNode.__init__(self, *args)
		try: self.label
		except: self.label = None

	def process_data(self, data):
		BaseNode.process_data(self, data)
		if 'caption' in data:
			self.label = QLabel(data['caption'])
			self.label.setAlignment(Qt.AlignLeft)
			self.layout.addWidget(self.label, self.y, self.x)
			self.y += 1


###################
## Views and co. ##
###################

class TableView(QTableView, BaseNode):
	def __init__(self, *args):
		super(QTableView, self).__init__()
		BaseNode.__init__(self, *args)
		self.setModel(self.view.model.data.current_table)
		self.sortByColumn(0, Qt.DescendingOrder)
		self.horizontalHeader().setSortIndicatorShown(True)
		self.setSortingEnabled(True)

	def process_data(self, data):
		if data is None: return

		BaseNode.process_data(self, data)
		if 'markup' in data:
			self.markup = data['markup']


class TabsView(QTabWidget, BaseNode):
	def __init__(self, *args):
		super(QTabWidget, self).__init__()
		BaseNode.__init__(self, *args)

	def process_data(self, data):
		BaseNode.process_data(self, data)
		if 'markups' in data:
			for tab in data['markups']:
				group = QGroupBox(self)
				group.setFlat(True)
				lay = Layout(self.view, group, node_type=0)
				lay.markup = tab
				try: title = lay.markup['title']
				except: title = 'Tab'
				self.addTab(group, title)


class InspectorView(QTreeWidget, BaseNode):
	def __init__(self, window, *args):
		super(QTreeWidget, self).__init__(window)
		BaseNode.__init__(self, window, *args)
		self.setColumnCount(1)
		self.setHeaderLabel('Tables:')
		self.itemDoubleClicked.connect(self.changeTable)
		self.icon = QIcon('icons/table.png')
		self.model = self.window.app.model
		self.model.registerWatcher(self)

	def handleUpdate(self, model, *args):
		items = []
		for x in model.db.tables():
			item = QTreeWidgetItem(self, [x])
			item.setIcon(0, self.icon)
			items.append(item)
		self.insertTopLevelItems(0, items)

	def changeTable(self, item):
		self.model.changeTable(item.text(0))


class BaseView(BaseNode):
	def __init__(self, *args):
		super().__init__(*args)
		self.layout = Layout(self.window, self, node_type=0)

	@property
	def markup(self):
		return self.layout.markup

	@markup.setter
	def markup(self, value):
		self.layout.markup = value
		self.window.handleUpdate()

	def handleUpdate(self):
		self.repaint()


class WorkspaceView(BaseView):
	def __init__(self, *args):
		super().__init__(*args)

	# def updateById(self, key, *args):
	# 	if key in self.nodes:
	# 		self.nodes[key].handleUpdate(*args)


class ModalWindow(QDialog, BaseView):
	def __init__(self, parent, title, w, h, *args):
		super(QDialog, self).__init__(parent, Qt.WindowCloseButtonHint)
		BaseView.__init__(self, parent, *args)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.setWindowTitle(title)
		self.setModal(True)
		self.resize(w, h)
		self.show()


generateNode = MappingList({
	'input': InputField,
	'textarea': TextArea,
	'button': Button,
	'layout': Layout,
	'inspector': InspectorView,
	'table': TableView,
	'tabs': TabsView
})