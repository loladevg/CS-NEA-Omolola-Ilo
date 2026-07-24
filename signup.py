# importing needed libraries and modules
from PyQt6.QtWidgets import QMainWindow, QMessageBox
import sqlite3
import hashlib
import re

# importing classes from the pyqt6 index ui file
from ui_qt6.ui_sign import Ui_MainWindow

# import python files to link to new window
import homepage 
import index



class SignoutPage(QMainWindow):
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
        # collects the name of the area for user to enter username/password directly from the ui file
        username = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()

        # function to hash the password entered above
        def hash_pass(pwd):
            return hashlib.sha256(pwd.encode()).hexdigest()

        # checks if the username or passwords input spaces are empty
        if username == "" or password == "":
            QMessageBox.warning(self, 'Error', "Username or Password is empty!")
            return None

        # checks if the username is less than 4 characters
        if len(username) < 4:
            QMessageBox.warning(self, 'Error', "Username is too short!")
            return None

        # to check if the value entered meets he outlined conditions
        def valid_password(pwd):
            # checks the length of the password
            if len(pwd) < 8:
                QMessageBox.warning(self, 'Error', "Password must contain at least 8 characters!")
                return False
            # checks if the password has any capital letters
            elif not re.search(r"[A-Z]", pwd):
                QMessageBox.warning(self, 'Error', "Password must include uppercase letters!")
                return False
            # checks if the password has any small letters
            elif not re.search(r"[a-z]", pwd):
                QMessageBox.warning(self, 'Error', "Password must include lowercase letters!")
                return False
            # checks if the password has any numbers
            elif not re.search(r"[0-9]+", pwd):
                QMessageBox.warning(self, 'Error', "Password must include digits!")
                return False
            # checks if the password has any special characters
            elif not re.search(r"[!@#$%^&*()¢∞§¶•ªº,.?\":{}|<>/']", pwd):
                QMessageBox.warning(self, 'Error', "Password must include special characters!")
                return False
            else:
                return True

        # queries database to check if another 'person' has already taken the username
        def check_username(user):
            with sqlite3.connect('data/database.db') as connection:
                crsor = connection.cursor()
                # checking for matching case
                crsor.execute("SELECT 1 FROM main.Account WHERE username = ?", (user,))
                exists = crsor.fetchone() is not None
            # if does not meet the criteria for username to be valid
            if exists:
                QMessageBox.warning(self, 'Error', "Username already exists!")
                return True
            return None

        # to store the result of the hashed version of password the user has entered
        hashed_password = hash_pass(password)

        if valid_password(password) and not check_username(username):
            # stores both the username and the hashed password value in the database
            with sqlite3.connect('data/database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO main.Account (username, hash_pass) VALUES (?, ?)",
                               (username, hashed_password))
                user_id = cursor.lastrowid

            QMessageBox.information(self, 'Success', "Account created successfully!")

            # opens to the homepage
            self.homeWin = homepage.HomePage(user_id)
            # the window for the homepage appears after verification
            self.homeWin.show()
            # this signup page closes
            self.close()
            return None
        return None

    # allows user to return back to start-up page
    def go_back(self):
        self.startWin.show()
        # after showing the index page, this signup page will close
        self.close()
