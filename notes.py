# import sqlite3 library
import sqlite3

# importing needed libraries and modules
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtGui import QTextCharFormat, QFont

# importing classes from the pyqt6 index ui file
from ui_qt6.ui_note import Ui_MainWindow



# define a MainWindow class that inherits from QMainWindow in .ui file
class WrNotes(QMainWindow):
    def __init__(self, home, user_id, note_id = None):
        # able to access 'classes' from the QMainWindow in index.ui file
        super().__init__()
        self.homeWin = home
        self.user_id = user_id
        self.note_id = note_id

        # initialising the QMainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.load_note()

        # access buttons by their object name, then connect each button 'click' event to a method
        self.ui.pushButton_2.clicked.connect(self.save_note)

        # user click on to make text bold, and off to disable
        self.ui.pushButton_3.setCheckable(True)
        self.ui.pushButton_3.toggled.connect(self.bold)

        # user click on to underline text, and off to disable
        self.ui.pushButton_4.setCheckable(True)
        self.ui.pushButton_4.toggled.connect(self.underline)

        # user click on to make text italics, and off to disable
        self.ui.pushButton_5.setCheckable(True)
        self.ui.pushButton_5.toggled.connect(self.italics)

        # user click on to make text bigger, and off to disable
        self.ui.pushButton_6.setCheckable(True)
        self.ui.pushButton_6.toggled.connect(self.head2)

        self.ui.pushButton_8.setCheckable(True)
        self.ui.pushButton_8.toggled.connect(self.go_back)


    def save_note(self):
        # collects the name of the area for user to enter header/text/'folder' directly from the ui file
        header = self.ui.lineEdit.text()
        texting = self.ui.textEdit.toHtml()
        folder = self.ui.lineEdit_2.text()

        # checks if the space for writing is empty
        if header == "" or texting == "":
            QMessageBox.critical(self, "Error", "Please fill all fields")
            return None

        # enters the information the user has entered into the database to store it
        with sqlite3.connect("data/database.db") as connection:
            cur = connection.cursor()
            if self.note_id is None:
                cur.execute(
                    "INSERT INTO main.Notes (heading, content, folder_name, user_id) VALUES (?, ?, ?, ?)",
                    (header, texting, folder, self.user_id))
                cur.execute("SELECT last_insert_rowid()")
                self.note_id = cur.fetchone()[0]
            else:
                cur.execute(
                    "UPDATE main.Notes SET heading = ?, content = ?, folder_name = ? WHERE note_id = ? AND user_id = ?",
                    (header, texting, folder, self.note_id, self.user_id))
        QMessageBox.information(self, "Success", "Notes saved")

        # after the information has been saved, the user is taken back to the homepage
        self.homeWin.load_notes()
        self.close()
        self.homeWin.show()
        return None

    def load_note(self):
        # when the note is clicked from the homepage, the data the user put down is to be shown in the note page layout
        with sqlite3.connect("data/database.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT heading, content, folder_name FROM main.Notes WHERE note_id = ? AND user_id = ?",
                (self.note_id, self.user_id))
            row = cur.fetchone()

        # if it returns something
        if row:
            heading, content, folder = row
            self.ui.lineEdit.setText(heading)
            self.ui.textEdit.setHtml(content)
            self.ui.lineEdit_2.setText(folder)

    def bold(self, bld):
        # to change the font state to bold
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if bld else QFont.Weight.Normal)
        cursor = self.ui.textEdit.textCursor()
        cursor.mergeCharFormat(fmt)
        self.ui.textEdit.mergeCurrentCharFormat(fmt)

    def underline(self, line):
        # to change the font state to underline
        fmt = QTextCharFormat()
        fmt.setFontUnderline(line)
        cursor = self.ui.textEdit.textCursor()
        cursor.mergeCharFormat(fmt)
        self.ui.textEdit.mergeCurrentCharFormat(fmt)

    def italics(self, italc):
        # to change the font state to italics
        fmt = QTextCharFormat()
        fmt.setFontItalic(italc)
        cursor = self.ui.textEdit.textCursor()
        cursor.mergeCharFormat(fmt)
        self.ui.textEdit.mergeCurrentCharFormat(fmt)

    def head2(self, head2):
        # to change/increase the font size
        fmt = QTextCharFormat()
        fmt.setFontPointSize(17 if head2 else 15)
        fmt.setFontUnderline(False)
        cursor = self.ui.textEdit.textCursor()
        cursor.mergeCharFormat(fmt)
        self.ui.textEdit.mergeCurrentCharFormat(fmt)

    def go_back(self):
        # to go back to the homepage
        self.close()
        self.homeWin.show()
