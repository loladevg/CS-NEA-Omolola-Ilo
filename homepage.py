# importing needed libraries and modules
import sqlite3
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QMainWindow, QListWidgetItem, QWidget, QHBoxLayout, QLabel, QMessageBox, QCheckBox

# importing classes from the pyqt6 index ui file
from ui_qt6.ui_home import Ui_MainWindow
from tasks import WrTasks

# import python files to link to new window
import settings
import notes



# define a MainWindow class that inherits from QMainWindow in .ui file
class HomePage(QMainWindow):
    def __init__(self, user_id):
        # able to access 'classes' from the QMainWindow in index.ui file
        super().__init__()
        self.user_id = user_id
        self.setWin = settings.Accounnt(self, self.user_id)
        # this is used when trying to sort the notes in (reverse) order
        self.sort_up = True

        # initialising the QMainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # this is so that when the user first opens the window their existing notes can be shown
        self.load_notes()

        # access buttons by their object name, then connect each button 'click' event to a method
        self.ui.pushButton_2.clicked.connect(self.sorting)
        self.ui.pushButton_5.clicked.connect(self.view_folder)
        self.ui.pushButton_6.clicked.connect(self.add_task)
        self.ui.pushButton_9.clicked.connect(self.new_note)
        self.ui.pushButton_10.clicked.connect(self.setting)

        # access the space for user to enter text into search bar from the ui in order to make use of function
        self.ui.lineEdit.textChanged.connect(self.filter_notes)

        # access the space for when the user clicks the notes fo them to expand and open
        self.ui.listWidget.itemClicked.connect(self.open_note)


    # used for sorting the notes in ascending to descending order, and vice versa
    def sorting(self):
        self.sort_up = not self.sort_up
        self.load_notes()

        # able to check the status of the order of the notes to arrange them in the expected way when sorting button is
        # clicked
        if self.sort_up:
            mode = "Oldest First"
        else:
            mode = "Newest First"

        self.sort_msg(f"Sorting: {mode}")

    def view_folder(self):
        # able to open the categories file
        self.setWin.catWin.folder_info()
        self.setWin.catWin.show()
        self.close()

    def add_task(self):
        # to be used in tasks window to store task in database for user
        self.setWin.taskWin = WrTasks(self.user_id, self)
        self.setWin.windows.append(self.setWin.taskWin)

        # to apply the current "theme" light mode or dark mode to the tasks list page
        if self.setWin.ui.frame_2.styleSheet():
            self.setWin.taskWin.ui.frame_2.setStyleSheet(self.setWin.ui.frame_2.styleSheet())

        # opens the task window
        self.setWin.taskWin.show()
        self.close()

    def new_note(self):
        self.setWin.noteWin = notes.WrNotes(self, self.user_id)
        self.setWin.windows.append(self.setWin.noteWin)

        # to apply the current "theme" light mode or dark mode to every newly created note
        if self.setWin.ui.frame_2.styleSheet():
            self.setWin.noteWin.ui.frame_2.setStyleSheet(self.setWin.ui.frame_2.styleSheet())

        # opens a new note window
        self.setWin.noteWin.show()
        self.close()

    def setting(self):
        # hides the current homepage to open the settings window
        self.hide()
        self.setWin.show()


    def filter_notes(self):
        # to be used to search for notes with similar titles
        search_text = self.ui.lineEdit.text().strip().lower()

        # 'removes' any text in the listWidget showing all the notes
        self.ui.listWidget.clear()

        # query database to check for the heading of notes to see if it matches the user input into the search bar
        with sqlite3.connect("data/database.db") as conn:
            cur = conn.cursor()
            # if the user has inputted something into the search bar 'respond'
            if search_text:
                cur.execute(
                    """SELECT note_id, heading 
                            FROM main.Notes 
                            WHERE user_id = ? AND LOWER(heading) LIKE ? 
                            ORDER BY note_id ASC""", (self.user_id, f"%{search_text}%"))
            # user has not entered anything into the search bar
            else:
                cur.execute("""SELECT note_id, heading 
                                    FROM main.Notes 
                                    WHERE user_id = ? 
                                    ORDER BY note_id ASC""", (self.user_id,))
            note = cur.fetchall()

        for note_id, heading in note:
            self.note_btn(note_id, heading)

    def load_notes(self):
        self.ui.listWidget.clear()

        # to be able to sort the notes in order
        # sort_up is true is asc order, else, is desc order
        with sqlite3.connect("data/database.db") as conn:
            cur = conn.cursor()
            if self.sort_up:
                order = "ASC"
            else:
                order = "DESC"
            cur.execute(f"SELECT note_id, heading "
                             f"FROM main.Notes "
                             f"WHERE user_id = ? "
                             f"ORDER BY note_id {order}", (self.user_id,))
            note = cur.fetchall()

        for note_id, heading in note:
            self.note_btn(note_id, heading)

    def note_btn(self, note_id, heading):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, note_id)
        self.ui.listWidget.addItem(item)

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # uses a checkbox to delete the note
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.del_note)

        # design for the 'label' with the user's note heading
        label = QLabel(heading)
        label.setStyleSheet("""
            QLabel {
                background-color: #202020;
                border: 1px solid #636363;
                border-radius: 15px;
                padding: 7px;
                margin: 2px;
                color: #cbcbcb;
                font-family: 'Quicksand';
                font-size: 15px;
            }
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # adding features to the note buton for the homepage like the checkbox and actual title to clik on
        layout.addWidget(checkbox)
        layout.addWidget(label)
        layout.addStretch()

        item.setSizeHint(widget.sizeHint())
        self.ui.listWidget.setItemWidget(item, widget)

    def del_note(self, state):
        # user is able to delete notes by clicking the checkboxes
        if state != 2:
            return None

        checkbox = self.sender()

        # checking for which task it is and then removing it from both the user's view and from the database
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            widget = self.ui.listWidget.itemWidget(item)

            if widget and checkbox in widget.findChildren(QCheckBox):
                with sqlite3.connect("data/database.db") as conn:
                    cur = conn.cursor()
                    note_id = item.data(Qt.ItemDataRole.UserRole)
                    cur.execute("DELETE FROM main.Notes WHERE note_id = ?", (note_id,))

                self.ui.listWidget.takeItem(i)
                return None
        return None

    def sort_msg(self, text):
        # message to show up after the notes have been sorted into order
        msg = QMessageBox(self)
        msg.setWindowTitle("Sorting Order")
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg.show()
        QTimer.singleShot(2000, msg.close)

    def open_note(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)

        # opens the notes window for each title
        self.setWin.noteWin = notes.WrNotes(self, self.user_id, note_id)
        self.setWin.windows.append(self.setWin.noteWin)

        # to be able to accept the changes to the background color
        self.setWin.noteWin.show()
        self.close()
