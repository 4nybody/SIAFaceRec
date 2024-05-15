import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QLineEdit, QVBoxLayout, QLabel, QPushButton
from PyQt5.uic import loadUi
from trackerwindow import TrackerWindow
from database_connector import DatabaseConnector
from PyQt5.QtCore import pyqtSignal


class AdminLoginDialog(QDialog):
	my_signal = pyqtSignal()

	def __init__(self):
		super().__init__()
		self.setWindowTitle("Admin Login")

		layout = QVBoxLayout()
		self.username_edit = QLineEdit()
		self.password_edit = QLineEdit()
		self.password_edit.setEchoMode(QLineEdit.Password)
		submit_button = QPushButton("Submit")
		submit_button.clicked.connect(self.submit_clicked)

		layout.addWidget(QLabel("Admin Username:"))
		layout.addWidget(self.username_edit)
		layout.addWidget(QLabel("Admin Password:"))
		layout.addWidget(self.password_edit)
		layout.addWidget(submit_button)

		self.setLayout(layout)

		# Database connection initialization
		self.database_connector = DatabaseConnector(
			host='localhost',
			user='root',
			password='Se@n_03!602',
			database='attendance'
		)

	def submit_clicked(self):
		admin_username = self.username_edit.text()
		admin_password = self.password_edit.text()

		# Query the database to check if the admin username and password are correct
		query = "SELECT username FROM admin WHERE username = %s AND password = %s"
		result = self.database_connector.fetch_one(query, (admin_username, admin_password))

		if result:
			self.my_signal.emit()
			self.accept()
		else:
			QMessageBox.warning(self, "Login Failed", "Invalid admin username or password. Please try again.")


class UpdatePasswordDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Update Password")

		layout = QVBoxLayout()
		self.username_edit = QLineEdit()
		self.new_password_edit = QLineEdit()
		self.retype_password_edit = QLineEdit()
		self.new_password_edit.setEchoMode(QLineEdit.Password)
		self.retype_password_edit.setEchoMode(QLineEdit.Password)
		submit_button = QPushButton("Submit")
		submit_button.clicked.connect(self.submit_clicked)

		layout.addWidget(QLabel("Username:"))
		layout.addWidget(self.username_edit)
		layout.addWidget(QLabel("New Password:"))
		layout.addWidget(self.new_password_edit)
		layout.addWidget(QLabel("Retype Password:"))
		layout.addWidget(self.retype_password_edit)
		layout.addWidget(submit_button)

		self.setLayout(layout)

	def submit_clicked(self):
		username = self.username_edit.text()
		new_password = self.new_password_edit.text()
		retype_password = self.retype_password_edit.text()

		# Ensure both username, new_password, and retype_password are not empty
		if not username:
			QMessageBox.warning(self, "Error", "Username is required.")
			return
		if not new_password:
			QMessageBox.warning(self, "Error", "New password is required.")
			return
		if not retype_password:
			QMessageBox.warning(self, "Error", "Please retype the new password.")
			return

		# Check if new password and retype password match
		if new_password != retype_password:
			QMessageBox.warning(self, "Error", "New password and retype password do not match.")
			return

		# Update the password in the database for the specified username
		database_connector = DatabaseConnector(host='localhost', user='root', password='Se@n_03!602',
											   database='attendance')
		update_query = "UPDATE admin SET password = %s WHERE username = %s"
		try:
			database_connector.execute_query(update_query, (new_password, username))
			QMessageBox.information(self, "Success", "Password updated successfully.")
			self.accept()
		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to update password: {str(e)}")

class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("login.ui", self)
        self.loginbutton.clicked.connect(self.loginfunction)
        self.forgotpasswordbutton.clicked.connect(self.forgot_password_function)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.tracker_window = None

    def loginfunction(self):
        username = self.username.text()
        password = self.password.text()

        query = "SELECT username FROM admin WHERE username = %s AND password = %s"
        database_connector = DatabaseConnector(host='localhost', user='root', password='Se@n_03!602',
                                               database='attendance')
        result = database_connector.fetch_one(query, (username, password))

        if result:
            self.show_tracker_window(database_connector)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")

    def forgot_password_function(self):
        print("Forgot password function called")
        admin_dialog = AdminLoginDialog()
        if admin_dialog.exec_() == QDialog.Accepted:
            print("Admin login successful")
            # Admin authentication succeeded, open the password update dialog
            update_password_dialog = UpdatePasswordDialog()
            update_password_dialog.exec_()

    def show_tracker_window(self, database_connector):
        self.tracker_window = TrackerWindow(database_connector)
        self.tracker_window.logged_out.connect(self.handle_logout)  # Connect logout signal
        self.tracker_window.show()
        self.hide()  # Hide the login dialog, instead of closing it

    def handle_logout(self):
        # Reset the login fields and show the login dialog again
        self.tracker_window.close()
        self.username.clear()
        self.password.clear()
        self.show()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	login_window = Login()
	login_window.show()
	sys.exit(app.exec_())
