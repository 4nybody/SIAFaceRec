import sys
import csv
from PyQt5.QtWidgets import QFileDialog, QPushButton, QHBoxLayout
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from database_connector import DatabaseConnector
from CreateNew import create_new_user
from PyQt5.QtCore import pyqtSignal


class DatabaseThread(QtCore.QThread):
	data_updated = QtCore.pyqtSignal(list)

	def __init__(self, database_connector):
		super(DatabaseThread, self).__init__()
		self.database_connector = database_connector

	def run(self):
		try:
			# Close and reopen the database connection
			self.database_connector.close_connection()
			self.database_connector.open_connection()

			print("Querying data from database...")
			query = """
				SELECT u.id, u.name, a.date_time, a.action, a.late, a.absent
				FROM attendance a
				JOIN users u ON a.user_id = u.id
				ORDER BY a.date_time DESC
			"""
			data = self.database_connector.fetch_all(query)

			# Print fetched data in the console
			print(f"Fetched data: {data}")

			self.data_updated.emit(data)
			print("Data queried successfully.")

		except Exception as e:
			print(f"Error querying data from database: {str(e)}")
		finally:
			# Always close the database connection after use
			self.database_connector.close_connection()



class TrackerWindow(QDialog):
	user_clocked_in_out_signal = QtCore.pyqtSignal()
	logged_out = pyqtSignal()

	def __init__(self, database_connector):
		super(TrackerWindow, self).__init__()
		loadUi("trackerwindow.ui", self)

		# Connect the signal to update the table
		self.user_clocked_in_out_signal.connect(self.populate_table_from_database)

		# Initialize the database connector
		self.database_connector = database_connector

		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.on_timer_timeout)
		self.timer.start(5000)  # Set the timeout interval to 5000 milliseconds (5 seconds)

		# Populate the table from the database
		self.populate_table_from_database()

		# Add export buttons
		self.export_button.clicked.connect(self.export_to_csv)
		self.createbutton.clicked.connect(self.createfunction)
		self.pushButton_logout.clicked.connect(self.logout_clicked)  # Connect logout button

	def logout_clicked(self):
		# Emit a signal to indicate logout
		self.logged_out.emit()

	def on_timer_timeout(self):
		print("Timer timeout triggered!")
		# Emit the signal to update the table
		self.user_clocked_in_out_signal.emit()

	def createfunction(self):
		self.create_window()
		# Emit the signal to update the table
		self.user_clocked_in_out_signal.emit()

	def create_window(self):
		self.create_window_instance = create_new_user()
		self.create_window_instance.show()

	def populate_table_from_database(self):
		try:
			print("Querying data from database...")

			# Create a new instance of DatabaseConnector
			db_config = {
				'host': 'localhost',
				'user': 'root',
				'password': 'Se@n_03!602',
				'database': 'attendance'
			}
			database_connector = DatabaseConnector(**db_config)

			query = """
				SELECT u.id, u.name, a.date_time, a.elapsed_time, a.action, a.late, a.absent
				FROM attendance a
				JOIN users u ON a.user_id = u.id
				ORDER BY a.date_time DESC
			"""
			data = database_connector.fetch_all(query)

			# Close the connection explicitly
			database_connector.close_connection()

			# Print fetched data in the console
			print(f"Fetched data: {data}")

			print("Updating table with new data...")
			# Now, populate the table with the fetched data
			self.tableWidget.setRowCount(len(data))
			self.tableWidget.setColumnCount(len(data[0]))  # Assuming all rows have the same number of columns

			for row_num, row_data in enumerate(data):
				for col_num, col_data in enumerate(row_data):
					item = QtWidgets.QTableWidgetItem(str(col_data))
					self.tableWidget.setItem(row_num, col_num, item)

			print("Table updated successfully.")

			# Add this line to force GUI update
			QtWidgets.QApplication.processEvents()

		except Exception as e:
			print(f"Error updating table: {str(e)}")

	def export_to_csv(self):
		filename, _ = QFileDialog.getSaveFileName(self, "Save as CSV", "", "CSV Files (*.csv)")
		if filename:
			try:
				with open(filename, 'w', newline='') as file:
					writer = csv.writer(file)
					# Write headers
					headers = [self.tableWidget.horizontalHeaderItem(i).text() for i in
							   range(self.tableWidget.columnCount())]
					writer.writerow(headers)
					# Write data
					for row in range(self.tableWidget.rowCount()):
						row_data = [self.tableWidget.item(row, col).text() for col in
									range(self.tableWidget.columnCount())]
						writer.writerow(row_data)
				QMessageBox.information(self, "Export Successful", f"Data exported to {filename} successfully.")
			except Exception as e:
				QMessageBox.warning(self, "Export Failed", f"Failed to export data: {str(e)}")


if __name__ == "__main__":
	app = QApplication(sys.argv)
	# Initialize the database connector
	db_config = {
		'host': 'localhost',
		'user': 'root',
		'password': 'Se@n_03!602',
		'database': 'attendance'
	}
	database_connector = DatabaseConnector(**db_config)
	tracker_window = TrackerWindow(database_connector)
	tracker_window.show()
	sys.exit(app.exec_())

