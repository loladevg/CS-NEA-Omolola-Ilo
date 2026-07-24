# import sqlite3 library
import sqlite3

# importing needed libraries and modules
import hashlib
from PyQt6.QtWidgets import QMainWindow, QMessageBox

# importing classes from the pyqt6 index ui file
from ui_qt6.ui_log import Ui_MainWindow

# import python files to link to new window
import homepage
import index



class LoginPage(QMainWindow):
    def __init__(self):
        # able to access 'classes' from the QMainWindow in index.ui file
        super().__init__()
        self.homeWin = None
        self.startWin = index.FrontPage()

        # initialising the QMainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # access buttons by their object name, then connect each button 'click' event to a method
        self.ui.pushButton.clicked.connect(self.open_home)
        self.ui.pushButton_2.clicked.connect(self.go_back)


    # 'event' to occur when the SignUp button is clicked
    def open_home(self):
        # collects the name of the area for user to enter username/password/hashed value directly from the ui file
        username = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        hashing = hashlib.sha256(password.encode()).hexdigest()

        # checks if the space for the username/password is empty
        if username == "" or password == "":
            QMessageBox.warning(self, 'Error', "Please enter username or password!")

        # queries the database to check for th existence of the entered username/hashed password
        with sqlite3.connect('data/database.db') as conn:
            cur = conn.cursor()
            check_pass = cur.execute("SELECT user_id, hash_pass FROM main.Account WHERE username = ?",
                                     (username,)).fetchone()

        # what to do if the username is not in the database
        if check_pass is None:
            QMessageBox.warning(self, 'Error', "Wrong username or password!")
            return None

        user_id = check_pass[0]
        hashed = check_pass[1]

        # checks if the hashed version if the password inputted matches the one assigned to the username in the database
        if hashed == hashing:
            QMessageBox.information(self, 'Success', "Login successful!")

            # stores the user id to be used in later sections
            self.homeWin = homepage.HomePage(user_id)
            self.homeWin.show()
            self.close()
            return None
        else:
            # if the hashed password does nto work
            QMessageBox.warning(self, 'Error', "Wrong username or password!")
            return None

    # allows user to return back to homepage
    def go_back(self):
        self.startWin.show()
        # after showing the index page, this login page will close
        self.close()
