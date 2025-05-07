import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QCheckBox, QLabel, QCalendarWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from google_calendar_adapter import GoogleCalendarAdapter


class ToDoCalendar(QWidget):
    def __init__(self):
        self.google_calendar = GoogleCalendarAdapter()
        
        super().__init__()
        self.setWindowTitle("ToDoCalendar")
        self.setGeometry(100, 100, 600, 500)

        self.json_file = "tasks.json"
        self.tasks_by_date = self.load_tasks()

        # Glowny layout
        main_layout = QHBoxLayout(self)

        # Lewy panel dla kalendarza i daty
        left_panel = QVBoxLayout()
        main_layout.addLayout(left_panel, stretch=1)
        

        # Data
        today = QDate.currentDate()
        self.current_date = today.toString("dd-MM-yyyy")
        formatted_date = today.toString("d MMMM yyyy")
        self.date_label = QLabel(formatted_date, self)
        self.date_label.setFont(QFont("Arial", 14))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.date_label)

        # Widget kalendarza
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.change_date)
        left_panel.addWidget(self.calendar)

        # Prawy panel dla kontrolek i taskow
        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel, stretch=2)

        # Pole inputowe
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Wpisz nazwę zadania...")
        right_panel.addWidget(self.task_input)

        # Przyciski
        self.add_task_button = QPushButton("Dodaj zadanie", self)
        self.add_task_button.setObjectName("add_task_button")
        self.add_task_button.clicked.connect(self.add_task)
        right_panel.addWidget(self.add_task_button)

        self.delete_task_button = QPushButton("Usuń wybrane zadanie", self)
        self.delete_task_button.setObjectName("delete_task_button")
        self.delete_task_button.clicked.connect(self.delete_task)
        right_panel.addWidget(self.delete_task_button)

        # Lista taskow
        self.task_list = QListWidget(self)
        right_panel.addWidget(self.task_list)

        # Ladowanie taskow na dzisiaj
        self.display_tasks_for_date(self.current_date)

    def load_tasks(self):
        try:
            with open(self.json_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_tasks(self):
        with open(self.json_file, "w") as file:
            json.dump(self.tasks_by_date, file, indent=4)

    def display_tasks_for_date(self, date):
        self.task_list.clear()
        tasks = self.tasks_by_date.get(date, [])
        for task_text in tasks:
            self.add_task_to_list_widget(task_text)

    def add_task_to_list_widget(self, task_text):
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)
        task_layout.setContentsMargins(0, 0, 0, 0)

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.toggle_task_completion)
        task_layout.addWidget(checkbox)

        task_label = QLineEdit(task_text)
        task_label.setReadOnly(True)
        task_layout.addWidget(task_label)

        item = QListWidgetItem(self.task_list)
        item.setSizeHint(task_widget.sizeHint())
        self.task_list.setItemWidget(item, task_widget)

    def add_task(self):
        task_text = self.task_input.text().strip()
        if task_text:
            if self.current_date not in self.tasks_by_date:
                self.tasks_by_date[self.current_date] = []
            self.tasks_by_date[self.current_date].append(task_text)
            self.save_tasks()

            self.add_task_to_list_widget(task_text)
            self.task_input.clear()

            # Dodanie zadania do Google Calendar
            date_obj = QDate.fromString(self.current_date, "dd-MM-yyyy")  
            google_date = date_obj.toString("yyyy-MM-dd")  # Konwersja na format Google Calendar  
            self.google_calendar.add_event(task_text, google_date)



    def delete_task(self):
        for i in range(self.task_list.count() - 1, -1, -1):
            item = self.task_list.item(i)
            task_widget = self.task_list.itemWidget(item)
            if task_widget:
                checkbox = task_widget.layout().itemAt(0).widget()
                if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                    task_label = task_widget.layout().itemAt(1).widget()
                    if isinstance(task_label, QLineEdit):
                        task_text = task_label.text()
                        if task_text in self.tasks_by_date.get(self.current_date, []):
                            self.tasks_by_date[self.current_date].remove(task_text)
                        self.save_tasks()
                        self.task_list.takeItem(i)

    def toggle_task_completion(self, state):
        checkbox = self.sender()
        if checkbox:
            task_widget = checkbox.parentWidget()
            if task_widget:
                task_label = task_widget.layout().itemAt(1).widget()
                if isinstance(task_label, QLineEdit):
                    if state == Qt.CheckState.Checked:
                        task_label.setFont(QFont(task_label.font().family(), task_label.font().pointSize(), QFont.Weight.Bold))
                        task_label.setStyleSheet("text-decoration: line-through; color: gray;")
                    else:
                        task_label.setFont(QFont(task_label.font().family(), task_label.font().pointSize(), QFont.Weight.Normal))
                        task_label.setStyleSheet("text-decoration: none; color: black;")

    def change_date(self, date):
        self.current_date = date.toString("dd-MM-yyyy")
        formatted_date = date.toString("d MMMM yyyy")
        self.date_label.setText(formatted_date)
        self.display_tasks_for_date(self.current_date)

    def load_stylesheet(self, filepath):
        try:
            with open(filepath, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Nie znaleziono pliku stylów: {filepath}")
