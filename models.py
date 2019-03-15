from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtCore import Qt, QAbstractItemModel


class DataModel(QAbstractItemModel):
	def __init__(self, app, driver, *args):
		super().__init__()
		self.db = QSqlDatabase.addDatabase(driver)
		self.app = app
		self.watchers = []
		self.table_model = TableModel(self)

	def openConnection(self, dbname=None, user=None, passwd=None, host=None, port=None):
		dbname = dbname or self.db.databaseName() or 'postgres'
		host = host or self.db.hostName() or 'localhost'
		port = port or self.db.port() or 5432
		user = user or self.db.userName() or 'postgres'
		passwd = passwd or self.db.password() or 'postgres'

		self.db.setHostName(host)
		self.db.setPort(port)
		self.db.setDatabaseName(dbname)
		self.db.setUserName(user)
		self.db.setPassword(passwd)
		self.closeConnection()
		if not self.db.open():
			print(self.db.lastError().text())
			return self
			# raise Exception("Error opening database: {0}".format(self.db.lastError().text()))
		self.changeTable(self.db.tables()[0])
		self.notifyWatchers()
		return self

	def closeConnection(self):
		if self.db.isOpen():
			self.notifyWatchers()
			self.db.close()

	def changeTable(self, table):
		self.table_model.setTable(table)
		self.table_model.handleUpdate()

	def registerWatcher(self, watcher):
		self.watchers.append(watcher)

	def notifyWatchers(self):
		for watch in self.watchers:
			watch.handleUpdate(self)


class TableModel(QSqlTableModel):
	def __init__(self, model, *args	):
		super().__init__(model.app, model.db, *args)
		self.app = model.app
		self.setSort(0, Qt.DescendingOrder)
		self.setEditStrategy(TableModel.OnRowChange)

	def submit(self):
		result = QSqlTableModel.submit(self)
		if not result:
			self.app.exception_handler('SQL', self.lastError().text())
			self.revert()
		return result

	def handleUpdate(self):
		self.select()


class Query:
	pass

class DatabaseGenerator:
	pass

class TableGenerator:
	pass

class QueryGenerator:
	pass
