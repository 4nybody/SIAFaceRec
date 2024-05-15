import sys
import random
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QPushButton, QLineEdit, QMessageBox
from PyQt5.uic import loadUi
import cv2
import os
from database_connector import DatabaseConnector

class create_new_user(QDialog):
    def __init__(self):
        super(create_new_user, self).__init__()
        loadUi("createnew.ui", self)

        self.webcam_label = self.findChild(QLabel, 'cam')
        self.createnew_button = self.findChild(QPushButton, 'createnewbutton')
        self.idnum_edit = self.findChild(QLineEdit, 'idnum')
        self.name_edit = self.findChild(QLineEdit, 'name')
        self.backbutton = self.findChild(QPushButton, 'backbutton')

        self.cam = cv2.VideoCapture(0)

        self.createnew_button.clicked.connect(self.show_new_user_window)
        self.backbutton.clicked.connect(self.back_to)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.process_webcam)
        self.timer.start(20)

        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Se@n_03!602',
            'database': 'attendance'
        }
        self.database_connector = DatabaseConnector(**db_config)

        self.recent_capture_arr = None

        self.database_dir = r'C:\Users\Sean\Desktop\SadSystemSIA\SadSystem\SADnaSystem\SADnaSystemExport\SADnaSystemExport\ImagesAttendance'
        if not os.path.exists(self.database_dir):
            os.mkdir(self.database_dir)

        # Generate a unique ID number and set it in the idnum_edit field
        self.idnum_edit.setText(self.generate_unique_id())

    def closeEvent(self, event):
        self.timer.stop()
        self.cam.release()
        self.database_connector.close_connection()
        event.accept()

    def back_to(self):
        self.close()

    def process_webcam(self):
        ret, frame = self.cam.read()
        self.recent_capture_arr = frame

        rgb_image = cv2.cvtColor(self.recent_capture_arr, cv2.COLOR_BGR2RGB)

        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width
        q_image = QtGui.QImage(rgb_image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)

        pixmap = QtGui.QPixmap.fromImage(q_image)
        self.webcam_label.setPixmap(pixmap)
        self.webcam_label.setScaledContents(True)

    def show_new_user_window(self):
        id_number = self.idnum_edit.text()
        name = self.name_edit.text()

        if not id_number:
            QMessageBox.warning(self, 'Error!', 'ID Number is required.')
            return
        if not name:
            QMessageBox.warning(self, 'Error!', 'Employee Name is required.')
            return

        if self.id_number_exists(id_number):
            QMessageBox.warning(self, 'Warning!', f'The ID number {id_number} already exists. Please try again.')
            return

        new_user_window = NewUserWindow(self, id_number, name)
        new_user_window.exec_()

    def generate_unique_id(self):
        while True:
            id_number = str(random.randint(1000, 9999))
            if not self.id_number_exists(id_number):
                return id_number

    def id_number_exists(self, id_number):
        query = "SELECT id FROM users WHERE id = %s"
        values = (id_number,)
        result = self.database_connector.fetch_one(query, values)
        return result is not None


class NewUserWindow(QDialog):
    def __init__(self, parent, id_number, name):
        super(NewUserWindow, self).__init__()
        loadUi("newuser.ui", self)

        self.parent = parent

        self.label = self.findChild(QLabel, 'capture')
        rgb_image = cv2.cvtColor(self.parent.recent_capture_arr, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width
        q_image = QtGui.QImage(rgb_image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(q_image)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

        self.label_id = self.findChild(QLabel, 'cap_id_num')
        self.label_name = self.findChild(QLabel, 'cap_name')

        self.label_id.setText(id_number)
        self.label_name.setText(name)

        self.submit_button = self.findChild(QPushButton, 'submitbutton')
        self.again_button = self.findChild(QPushButton, 'againbutton')

        self.submit_button.clicked.connect(self.submit_function)
        self.again_button.clicked.connect(self.again_function)

    def submit_function(self):
        id_number = self.parent.idnum_edit.text()
        name = self.parent.name_edit.text()

        if not id_number or not name:
            QMessageBox.warning(self, 'Error!', 'ID Number and Employee Name are required.')
            return

        if self.parent.id_number_exists(id_number):
            QMessageBox.warning(self, 'Warning!', f'The ID number {id_number} already exists. Please try again.')
            return

        try:
            # Save the image to the local directory
            image_path = os.path.join(self.parent.database_dir, f'{id_number}.jpg')
            cv2.imwrite(image_path, self.parent.recent_capture_arr)

            # Insert user data into the database
            self.parent.database_connector.create_user(id_number, name)

            QMessageBox.information(self, 'Success!', 'Registered User Successfully')
            self.close()
            self.parent.show()
        except Exception as e:
            QMessageBox.critical(self, 'Error!', f'Failed to save image or insert data into the database: {str(e)}')

    def again_function(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    create_window = create_new_user()
    create_window.show()
    sys.exit(app.exec_())
