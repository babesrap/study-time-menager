import json
import time
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QDoubleSpinBox, QPushButton, QMessageBox, QHBoxLayout, QComboBox
from PySide6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Klasy stanów
class TimerState:
    def start_timer(self, timer):
        pass

    def stop_timer(self, timer):
        pass

    def reset_timer(self, timer):
        pass

    def update_timer(self, timer):
        pass

class IdleState(TimerState):
    def start_timer(self, timer):
        if not timer.is_running:
            timer.time_elapsed = 0
            timer.target_time = int(timer.time_input.value() * 60)
            timer.start_time = time.time()
            timer.timer.start(1000)
            timer.is_running = True
            timer.time_input.hide()
            timer.current_state = RunningState()

class RunningState(TimerState):
    def stop_timer(self, timer):
        timer.timer.stop()
        timer.is_running = False
        timer.time_input.show()
        timer.current_state = IdleState()

    def reset_timer(self, timer):
        timer.timer.stop()
        timer.time_elapsed = 0
        timer.time_display.setText("00:00")
        timer.is_running = False
        timer.time_input.show()
        timer.current_state = IdleState()

    def update_timer(self, timer):
        if timer.time_elapsed < timer.target_time:
            timer.time_elapsed += 1
            minutes = timer.time_elapsed // 60
            seconds = timer.time_elapsed % 60
            timer.time_display.setText(f"{minutes:02}:{seconds:02}")
        else:
            timer.timer.stop()
            timer.is_running = False
            timer.add_points()
            timer.update_stats()
            timer.update_activities()
            timer.show_completion_message()
            timer.time_input.show()
            timer.current_state = CompletedState()

class CompletedState(TimerState):
    def start_timer(self, timer):
        timer.current_state = IdleState()
        timer.current_state.start_timer(timer)

# Główna klasa FocusTimer
class FocusTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.time_elapsed = 0
        self.is_running = False
        self.start_time = None
        self.points = 0
        self.activity = "Reading"
        self.activities = {"Reading": 0, "Coding": 0, "Studying": 0, "Relaxing": 0}
        self.current_state = IdleState()  # Początkowy stan
        self.load_points()
        self.load_activities()
        self.initUI()
        self.load_stylesheet()

    def initUI(self):
        layout = QVBoxLayout()

        self.time_display = QLabel("00:00", self)
        layout.addWidget(self.time_display)

        # Activity selection
        self.activity_selector = QComboBox(self)
        self.activity_selector.addItems(self.activities.keys())
        self.activity_selector.currentTextChanged.connect(self.set_activity)
        layout.addWidget(self.activity_selector)

        # Predefined time buttons
        button_layout = QHBoxLayout()
        self.add_time_button(button_layout, "1 min", 1)
        self.add_time_button(button_layout, "5 min", 5)
        self.add_time_button(button_layout, "10 min", 10)
        self.add_time_button(button_layout, "15 min", 15)
        self.add_time_button(button_layout, "30 min", 30)
        layout.addLayout(button_layout)

        # Custom time input
        self.time_input = QDoubleSpinBox(self)
        self.time_input.setRange(0.5, 120)
        self.time_input.setSingleStep(0.5)
        self.time_input.setSuffix(" min")
        layout.addWidget(self.time_input)

        self.start_button = QPushButton("Start", self)
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.clicked.connect(self.confirm_stop_timer)
        layout.addWidget(self.stop_button)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setObjectName("reset_button")
        self.reset_button.clicked.connect(self.confirm_reset_timer)
        layout.addWidget(self.reset_button)

        self.stats_button = QPushButton("Show Stats", self)
        self.stats_button.setObjectName("stats_button")
        self.stats_button.clicked.connect(self.show_stats)
        layout.addWidget(self.stats_button)

        self.points_display = QLabel(f"Points: {self.points}", self)
        layout.addWidget(self.points_display)

        # Pie chart
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.update_pie_chart()

        self.setLayout(layout)
        self.setWindowTitle("Focus Timer")

    def load_stylesheet(self):
        with open("styles.qss", "r") as file:
            self.setStyleSheet(file.read())

    def add_time_button(self, layout, label, minutes):
        button = QPushButton(label, self)
        button.clicked.connect(lambda: self.set_timer(minutes))
        layout.addWidget(button)

    def set_activity(self, activity):
        self.activity = activity

    def set_timer(self, minutes):
        self.time_input.setValue(minutes)
        self.start_timer()

    # Metody związane ze stanami
    def start_timer(self):
        self.current_state.start_timer(self)

    def stop_timer(self):
        self.current_state.stop_timer(self)

    def reset_timer(self):
        self.current_state.reset_timer(self)

    def update_timer(self):
        self.current_state.update_timer(self)

    def confirm_stop_timer(self):
        if self.is_running:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setText("Really wanna stop? Don't give up!")
            msg_box.setWindowTitle("Confirm Stop")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            result = msg_box.exec()

            if result == QMessageBox.StandardButton.Yes:
                self.stop_timer()

    def confirm_reset_timer(self):
        if self.is_running:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setText("Are you sure you want to reset the timer?")
            msg_box.setWindowTitle("Confirm Reset")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
            result = msg_box.exec()

            if result == QMessageBox.StandardButton.Yes:
                self.reset_timer()

    def add_points(self):
        self.points += 10
        self.save_points()
        self.points_display.setText(f"Points: {self.points}")

    def save_points(self):
        with open("points.json", "w") as file:
            json.dump({"points": self.points}, file)

    def load_points(self):
        try:
            with open("points.json", "r") as file:
                data = json.load(file)
                self.points = data.get("points", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            self.points = 0

    def update_stats(self):
        try:
            with open("stats.json", "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    total_time = sum(data)
                    data = {"total_time": total_time}
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"total_time": 0}

        data["total_time"] += self.time_elapsed
        with open("stats.json", "w") as file:
            json.dump(data, file)

    def show_stats(self):
        try:
            with open("stats.json", "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    total_time = sum(data)
                    data = {"total_time": total_time}
                total_time = data.get("total_time", 0)
                minutes = total_time // 60
                seconds = total_time % 60
                self.time_display.setText(f"Total Focus Time: {minutes:02}:{seconds:02}")
        except (FileNotFoundError, json.JSONDecodeError):
            self.time_display.setText("Total Focus Time: 00:00")

    def show_completion_message(self):
        minutes = self.time_elapsed // 60
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(f"Timer ended. {minutes} minutes passed. Keep Going!")
        msg_box.setWindowTitle("Focus Timer")
        msg_box.exec()

    def update_activities(self):
        self.activities[self.activity] += self.time_elapsed // 60
        self.save_activities()
        self.update_pie_chart()

    def save_activities(self):
        with open("activities.json", "w") as file:
            json.dump(self.activities, file)

    def load_activities(self):
        try:
            with open("activities.json", "r") as file:
                self.activities = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.activities = {"Reading": 0, "Coding": 0, "Studying": 0, "Relaxing": 0}

    def update_pie_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        activities = list(self.activities.keys())
        times = list(self.activities.values())

        if sum(times) == 0:
            times = [1] * len(times)
        ax.pie(times, labels=activities, autopct='%1.1f%%', startangle=140)
        self.canvas.draw()
