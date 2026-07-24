# importing needed libraries and modules
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication

# importing classes from the pyqt6 index ui file
from ui_qt6.ui_index import Ui_MainWindow

# import python files to link to new window
import signup 
import login



class FrontPage(QMainWindow):
    def __init__(self): 
        # able to access 'classes' from the QMainWindow in index.ui file
        super().__init__()
        self.signup = None
        self.login = None

        # initialising the QMainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # access buttons by their object name, then connect each button 'click' event to a method from converted ui file
        self.ui.pushButton.clicked.connect(self.open_signup)
        self.ui.pushButton_2.clicked.connect(self.open_login)
    
    
    # 'event' to occur when the SignUp button is clicked
    def open_signup(self):
        # links to the signup window for the user to enter their details and 'hide' this index window
        self.signup = signup.SignoutPage()
        # to open the file and load window for signup page
        self.signup.show()
        # to hide this index page from view
        self.hide()
    
    # 'event' to occur when the LogIn button is clicked
    def open_login(self):
        # links to the login window for the user to enter their details and 'hide' this index window
        self.login = login.LoginPage()
        # to open the file and load window for login page
        self.login.show()
        # to hide this index page from view
        self.hide()



# will load the python file with all its 'interactions'
# so the python programs only run when this file has been run
if __name__ == "__main__":
    # creates the application to run
    app = QApplication(sys.argv)

    # loading the class and attributes within it
    window = FrontPage()
    window.show()

    # marks the end of the python file running
    sys.exit(app.exec())

