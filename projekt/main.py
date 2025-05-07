import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from focus_timer import FocusTimer
# from todocalendar import ToDoCalendar
from notes import Notes, SimpleObfuscator, ObfuscatedNotesDecorator
# from google_calendar_adapter import GoogleCalendarAdapter

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productivity App")
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # self.google_calendar = GoogleCalendarAdapter()

        self.focus_timer_tab = FocusTimer()
        # self.todo_calendar_tab = ToDoCalendar()

        # Tworzenie podstawowego komponentu notatek i dekorowanie go
        base_notes = Notes()
        obfuscator = SimpleObfuscator(key=123)
        self.notes_tab = ObfuscatedNotesDecorator(base_notes, obfuscator)

        self.tab_widget.addTab(self.focus_timer_tab, "Focus Timer")
        # self.tab_widget.addTab(self.todo_calendar_tab, "ToDoCalendar")
        self.tab_widget.addTab(self.notes_tab.widget, "Notes")

        self.load_stylesheet("styles.qss")

    def load_stylesheet(self, filepath):
        try:
            with open(filepath, "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Nie znaleziono pliku stylów: {filepath}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())