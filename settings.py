# importing needed libraries and modules
from PyQt6.QtWidgets import QMainWindow, QMessageBox

import notes
# importing classes from the pyqt6 index ui file
from ui_qt6.ui_sets import Ui_MainWindow

# import files to link to in other functions
import index
import tasks
import categories



# define a MainWindow class that inherits from QMainWindow in .ui file
class Accounnt(QMainWindow):
    def __init__(self, home, user_id):
        # able to access 'classes' from the QMainWindow in index.ui file
        super().__init__()
        self.startWin = index.FrontPage()
        self.homeWin = home
        self.user_id = user_id

        self.taskWin = tasks.WrTasks(self.user_id, home)
        self.noteWin = notes.WrNotes(home, self.user_id)
        self.catWin = categories.Folders(home, user_id)
        # this is the list of all the windows that will be able to change heme
        # i.e. the windows that can be accessed from the homepage window only
        # here fore excluding the index, signup and login pages
        self.windows = [self.homeWin, self.taskWin, self.catWin, self, self.noteWin]

        # initialising the QMainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # access buttons by their object name, then connect each button 'click' event to a method
        self.ui.pushButton.clicked.connect(self.light_mode)
        self.ui.pushButton_2.clicked.connect(self.dark_mode)
        self.ui.pushButton_3.clicked.connect(self.sign_out)
        self.ui.pushButton_4.clicked.connect(self.go_back)
        self.ui.pushButton_5.clicked.connect(self.del_user)


    def light_mode(self):
        # change background for all frame_2 background
        for win in self.windows:
            win.ui.frame_2.setStyleSheet("background-color: #C6BAB7; border: 1px solid #000000; border-radius: 33px;")

    def dark_mode(self):
        # change background for all frame_2 background back to the original theme style
        for win in self.windows:
            win.ui.frame_2.setStyleSheet("background-color: #393939; border: 1px solid #000000; border-radius: 33px;")
        self.homeWin.ui.frame_2.setStyleSheet("background-color: #433427; border: 1px solid #000000; border-radius: 33px;")

    def sign_out(self):
        # after showing the index page, this signup page will close
        self.close()
        self.startWin.show()

    def go_back(self):
        # button so the user can go back to the homepage, after closing the settings page
        self.close()
        self.homeWin.show()

    def del_user(self):
        # asks user if they want to delete their account, 'no' is the default button
        ask = (QMessageBox.question(self, "Delete Account", "Are you sure you want to delete your account?"),
               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        # if the user has chosen to delete their account
        if ask == QMessageBox.StandardButton.Yes:
            with sqlite3.connect("data/database.db") as conn:
                cur = conn.cursor()
                # delete user account for database by user_id
                cur.execute("DELETE FROM Users WHERE user_id = ?", (self.user_id,))
                # delete user linked notes from database by user_id
                cur.execute("DELETE FROM Notes WHERE user_id = ?", (self.user_id,))
                # delete user linked tasks from database by user_id
                cur.execute("DELETE FROM Tasks WHERE user_id = ?", (self.user_id,))

            # after deleting, return to login page or close app
            self.close()
            self.startWin.show()
