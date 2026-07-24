# importing needed libraries and modules
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QListWidgetItem, QWidget, QHBoxLayout, QCheckBox, QLabel, QInputDialog, \
        QMessageBox

# importing classes from the pyqt6 index ui file
from ui_qt6.ui_task import Ui_MainWindow



# define a MainWindow class that inherits from QMainWindow in .ui file
class WrTasks(QMainWindow):
    def __init__(self, user_id, home):
        # able to access 'classes' from the QMainWindow in index.ui file
        super().__init__()
        self.user_id = user_id
        self.homeWin = home

        # initialising the QMainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # this is so that when the user first opens the window their existing tasks can be shown
        self.load_tasks()

        # access buttons by their object name, then connect each button 'click' event to a method
        self.ui.pushButton_2.clicked.connect(self.save_task)
        self.ui.pushButton_3.clicked.connect(self.go_back)
        self.ui.pushButton_8.clicked.connect(self.add_task)


    # aims to add the new task to the database
    def save_task(self):
        with sqlite3.connect('data/database.db') as conn:
            crsor = conn.cursor()

            # checks through current tasks list to check for duplicates and insert new tasks
            for i in range(self.ui.listWidget.count()):
                item = self.ui.listWidget.item(i)
                widget = self.ui.listWidget.itemWidget(item)
                label = widget.findChild(QLabel)
                task_text = label.text().strip()

                # checks if there is anything entered into
                if task_text:
                    # checks if the task already exists
                    crsor.execute(
                        "SELECT 1 FROM main.Tasks WHERE content = ? AND user_id = ?",
                        (task_text, self.user_id))
                    exists = crsor.fetchone()
                    # if duplicates not in database
                    if not exists:
                        crsor.execute(
                        "INSERT INTO main.Tasks (content, user_id) VALUES (?, ?)",
                        (task_text, self.user_id))

        QMessageBox.information(self, "Tasks Saved", "Tasks Saved")

    def go_back(self):
        # user returns back to homepage
        self.homeWin.show()
        self.close()

    def add_task(self):
        # user is able to add new tasks to new or existing list continuously
        task_text, ok = QInputDialog.getText(self, "New Task", "Enter task name:")
        if not ok or not task_text.strip():
            return None

        task_text = task_text.strip()

        # checks for duplicate task 'names'
        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            widget = self.ui.listWidget.itemWidget(item)
            label = widget.findChild(QLabel)
            if label and label.text().strip().lower() == task_text.lower():
                QMessageBox.warning(self, "Duplicate Task", "This task already exists.")
                return None

        # to proceed if there is no copy of the task already available
        item = QListWidgetItem()
        self.ui.listWidget.addItem(item)

        # creates a widget containing the task name
        task_widget = QWidget()
        layout = QHBoxLayout(task_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # checkbox to mark if user wants to delete a task
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.del_task)

        # design for the label for the task name
        label = QLabel(task_text)
        label.setStyleSheet(""" 
            QLabel { 
                background-color: #202020; 
                border: 1px solid #636363; 
                border-radius: 15px; 
                padding: 7px; 
                color: #cbcbcb; 
                font-family: 'Quicksand'; 
                font-size: 15px; 
            } 
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # each line containing a checkbox and a label which expand depend on the length of the task
        layout.addWidget(checkbox)
        layout.addWidget(label)
        layout.addStretch()

        item.setSizeHint(task_widget.sizeHint())
        self.ui.listWidget.setItemWidget(item, task_widget)
        return None


    def del_task(self, state):
        # user is able to delete tasks by clicking the checkboxes
        if state != 2:
            return None

        checkbox = self.sender()

        for i in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(i)
            widget = self.ui.listWidget.itemWidget(item)

            # to remove the task from the database
            if widget and checkbox in widget.findChildren(QCheckBox):
                with sqlite3.connect('data/database.db') as conn:
                    cursor = conn.cursor()
                    task_id = item.data(Qt.ItemDataRole.UserRole)
                    cursor.execute("""DELETE FROM main.Tasks WHERE task_id = ?""", (task_id,))

                # removes from users view
                self.ui.listWidget.takeItem(i)
                return None
        return None

    # when the task page window is opened all the tasks for that user will appear here
    def load_tasks(self):
        with sqlite3.connect('data/database.db') as conn:
            crsor = conn.cursor()
            crsor.execute("SELECT task_id, content FROM main.Tasks WHERE user_id = ?", (self.user_id,))
            tasks = crsor.fetchall()

        for task_id, task_text in tasks:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, task_id)
            self.ui.listWidget.addItem(item)

            task_widget = QWidget()
            layout = QHBoxLayout(task_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            # showing the tasks checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.del_task)

            # the presentation of current tasks when he task window is opened
            label = QLabel(task_text)
            label.setStyleSheet(""" 
                QLabel { 
                    background-color: #202020; 
                    border: 1px solid #636363; 
                    border-radius: 15px; 
                    padding: 7px; 
                    color: #cbcbcb; 
                    font-family: 'Quicksand'; 
                    font-size: 15px; 
                    background-clip: padding;
                }  
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # each line containing a checkbox and a label which expand depend on the length of the task
            layout.addWidget(checkbox)
            layout.addWidget(label)
            layout.addStretch()

            item.setSizeHint(task_widget.sizeHint())
            self.ui.listWidget.setItemWidget(item, task_widget)
