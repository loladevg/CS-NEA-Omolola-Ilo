# importing needed libraries and modules
import sqlite3
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget, QInputDialog,
                             QListWidgetItem, QCheckBox, QLabel, QMessageBox)

# importing classes from the pyqt6 index ui file
from ui_qt6.ui_cat import Ui_MainWindow



# define a MainWindow class that inherits from QMainWindow in .ui file
class Folders(QMainWindow):
    def __init__(self, home, user_id):
        # able to access 'classes' from the QMainWindow in index.ui file
        super().__init__()
        self.homeWin = home
        self.user_id = user_id
        self.popup = None
        self.list_widget = None
        self.count = None
        self.sort_up = True

        # initialising the QMainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.folder_info()

        # access buttons by their object name, then connect each button 'click' event to a method
        self.ui.pushButton_3.clicked.connect(self.go_back)
        self.ui.pushButton_2.clicked.connect(self.sort_fldr)

        # space for when the user has a new folder and how to act with it
        self.ui.listWidget.itemClicked.connect(self.click_folder)


    def go_back(self):
        # button so the user can go back to the homepage, after closing the categories page
        self.close()
        # more specifically, this action is performed so that if a note for a folder is actually deleted
        # then the note doesn't appear on the user's homepage
        # acts as a "refresh" button
        self.homeWin.load_notes()
        self.homeWin.show()

    def sort_fldr(self):
        self.sort_up = not self.sort_up
        self.folder_info()

        # able to check the status of the notes in order to arrange them in the expected way when sorting button is clicked
        if self.sort_up:
            # if true, the tasks will be put into asc order, else, desc order
            mode = "Oldest First"
        else:
            mode = "Newest First"

        self.sort_msg(f"Sorting: {mode}")


    def folder_info(self):
        self.ui.listWidget.clear()

        if self.sort_up:
            order = "ASC"
        else:
            order = "DESC"

        with sqlite3.connect("data/database.db") as conn:
            cur = conn.cursor()
            cur.execute(
                f"""SELECT folder_name, COUNT(*) FROM main.Notes WHERE user_id = ? AND folder_name IS NOT 
            NULL AND folder_name != '' GROUP BY folder_name ORDER BY folder_name {order}""", (self.user_id,))
            folders = cur.fetchall()

        for folder_name, count in folders:
            self.add_folder(folder_name, count)

    def note_win(self, folder_name):
        # each time a new note is created a new line is created to show the heading of the note
        # the box acts as a link so that the user can view what they wrote in there
        self.popup = QMainWindow()
        self.popup.setWindowTitle(folder_name)

        container = QWidget()
        layout = QVBoxLayout(container)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # to return all he 'headings' the user has under their id
        with sqlite3.connect("data/database.db") as conn:
            cur = conn.cursor()
            cur.execute("""SELECT note_id, heading FROM main.Notes WHERE user_id = ? AND folder_name = ?""",
                        (self.user_id, folder_name))
            ntes = cur.fetchall()

        for note_id, heading in ntes:
            item = QListWidgetItem(heading)
            item.setData(Qt.ItemDataRole.UserRole, note_id)
            self.list_widget.addItem(item)

        # popup page to show
        # if the user wants to delete a particular note within the folder (after clicking on the folder name)R
        del_note = QPushButton("Delete Selected Note", self.popup)
        del_note.clicked.connect(self.del_note)
        layout.addWidget(del_note)

        # (same) popup page to show if the user wants to rename the folder (after clicking on the folder name)
        btn_rename = QPushButton("Rename Folder", self.popup)
        btn_rename.clicked.connect(lambda: self.rename_folder(folder_name))
        layout.addWidget(btn_rename)

        # size of the popup page
        self.popup.setCentralWidget(container)
        self.popup.adjustSize()
        self.popup.show()

    def del_note(self):
        if not self.list_widget:
            return None

        item = self.list_widget.currentItem()
        if not item:
            return None

        # gets the notes id
        note_id = item.data(Qt.ItemDataRole.UserRole)
        # query database for the note and then delete it from the database and changes user view to remove note
        with sqlite3.connect("data/database.db") as conn:
            cur = conn.cursor()
            cur.execute("""DELETE FROM main.Notes WHERE note_id = ? AND user_id = ?""",
                        (note_id, self.user_id))

        self.list_widget.takeItem(self.list_widget.row(item))
        self.folder_info()
        return None

    def add_folder(self, folder_name, count):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, folder_name)
        self.ui.listWidget.addItem(item)

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)

        # uses a checkbox to delete the folder
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.del_folder)

        # design for the 'label' with the user's folder named
        label = QLabel(f"{folder_name} ({count})")
        label.setStyleSheet("""
            background-color: #433427;
            border: 1px solid #636363;
            border-radius: 15px;
            padding: 15px; 
            color: #cbcbcb; 
            margin: 7px; 
            padding: 7px;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(checkbox)
        layout.addWidget(label)
        layout.addStretch()

        item.setSizeHint(row.sizeHint())
        self.ui.listWidget.setItemWidget(item, row)

    def del_folder(self, state):
        # checks if the checkbox has been marked before it goes ahead to delete the folder with its connected notes
        if state != 2:
            return None

        checkbox = self.sender()

        # checking for which note it is and then removing it from both the user's view and from the database
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            widget = self.ui.listWidget.itemWidget(item)

            if widget and checkbox in widget.findChildren(QCheckBox):
                folder_name = item.data(Qt.ItemDataRole.UserRole)

                with sqlite3.connect("data/database.db") as conn:
                    cur = conn.cursor()
                    cur.execute("""UPDATE main.Notes SET folder_name = '' WHERE user_id = ? AND folder_name = ? """,
                                (self.user_id, folder_name))

                self.ui.listWidget.takeItem(i)
                return None
        return None

    def rename_folder(self, old_folder_name):
        # when the user decides to change the name of their folder
        new_name, ok = QInputDialog.getText(self, "Rename Folder", "New folder name:")
        if not ok or not new_name.strip():
            return

        # to replace the former foldr name with the new one
        with sqlite3.connect("data/database.db") as conn:
            cur = conn.cursor()
            cur.execute("""UPDATE main.Notes SET folder_name = ? WHERE user_id = ? AND folder_name = ?""",
                        (new_name, self.user_id, old_folder_name))

        self.folder_info()

    def click_folder(self, item):
        widget = self.ui.listWidget.itemWidget(item)
        checkbox = widget.findChild(QCheckBox)

        # so the user can't mark the checkbox to show the notes
        if checkbox.underMouse():
            return None

        # if the user clicks the folder_name, then the popup showing the notes in the folder, will appear
        folder_name = item.data(Qt.ItemDataRole.UserRole)
        self.note_win(folder_name)
        return None

    def sort_msg(self, text):
        # message to show up after the folders have been sorted into order
        msg = QMessageBox(self)
        msg.setWindowTitle("Sorting Order")
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg.show()
        QTimer.singleShot(2000, msg.close)