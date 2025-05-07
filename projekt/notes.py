from typing import List, Dict, Any, Optional
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox, QListWidget, QListWidgetItem, QComboBox
)
from datetime import datetime
from abc import ABC, abstractmethod

# Interfejs dla notatek
class NotesInterface:
    """Interfejs dla notatek"""
    def load_notes(self) -> List[Any]:
        pass

    def save_notes(self) -> None:
        pass

    def save_note(self) -> None:
        pass

# Klasy strategii sortowania
class NoteSortStrategy:
    def sort(self, notes: List['Note']) -> List['Note']:
        pass

class SortByDate(NoteSortStrategy):
    def sort(self, notes: List['Note']) -> List['Note']:
        return sorted(notes, key=lambda note: note.date, reverse=True)


class SortByTitle(NoteSortStrategy):
    def sort(self, notes: List['Note']) -> List['Note']:
        return sorted(notes, key=lambda note: note.title.lower())

class SortByCategory(NoteSortStrategy):
    def sort(self, notes: List['Note']) -> List['Note']:
        return sorted(notes, key=lambda note: note.category.lower())

class SimpleObfuscator:
    def __init__(self, key: int):
        self.key = key

    def obfuscate(self, text: str) -> str:
        return ''.join(chr(ord(c) ^ self.key) for c in text)

    def deobfuscate(self, text: str) -> str:
        return ''.join(chr(ord(c) ^ self.key) for c in text)

class Note:
    def __init__(self, title: str, content: str, category: str, date: str):
        self.title = title
        self.content = content
        self.category = category
        self.date = date

    def save_data(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "date": self.date
        }

class NoteFactory:
    @staticmethod
    def create_note(category: str, title: str, content: str) -> Note:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return Note(title, content, category, current_date)

class Notes(QWidget, NotesInterface):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notes")
        self.setGeometry(100, 100, 800, 500)

        self.json_file: str = "notes.json"
        self.notes: List[Note] = self.load_notes()
        self.sort_strategy: NoteSortStrategy = SortByDate()  # Domyślna strategia

        main_layout = QHBoxLayout()

        # Lewy panel
        input_layout = QVBoxLayout()

        self.note_title = QLineEdit(self)
        self.note_title.setPlaceholderText("Title")
        input_layout.addWidget(self.note_title)

        self.note_content = QTextEdit(self)
        input_layout.addWidget(self.note_content)

        self.note_category = QComboBox(self)
        self.note_category.addItems(["Nauka", "Praca", "Kodowanie", "Zadania"])
        input_layout.addWidget(self.note_category)

        # Dodajemy wybór sortowania
        sort_layout = QHBoxLayout()
        self.sort_combo = QComboBox(self)
        self.sort_combo.addItems(["Sort by Date", "Sort by Title", "Sort by Category"])
        self.sort_combo.currentTextChanged.connect(self.change_sort_strategy)
        sort_layout.addWidget(self.sort_combo)

        sort_button = QPushButton("Sort", self)
        sort_button.clicked.connect(self.apply_sort)
        sort_layout.addWidget(sort_button)

        input_layout.addLayout(sort_layout)

        self.save_button = QPushButton("Save Note", self)
        self.save_button.setObjectName("save_note_button")
        self.save_button.clicked.connect(self.save_note)
        input_layout.addWidget(self.save_button)

        main_layout.addLayout(input_layout, 2)

        # Prawy panel
        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.load_note)
        main_layout.addWidget(self.notes_list, 1)

        self.setLayout(main_layout)
        self.refresh_notes_list()

    def change_sort_strategy(self, strategy_name: str) -> None:
        if strategy_name == "Sort by Date":
            self.sort_strategy = SortByDate()
        elif strategy_name == "Sort by Title":
            self.sort_strategy = SortByTitle()
        elif strategy_name == "Sort by Category":
            self.sort_strategy = SortByCategory()

    def apply_sort(self) -> None:
        self.notes = self.sort_strategy.sort(self.notes)
        self.refresh_notes_list()

    def load_notes(self) -> List[Note]:
        try:
            with open(self.json_file, "r") as file:
                data = json.load(file)
                return [self.create_note_from_data(note_data) for note_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def create_note_from_data(self, data: Dict[str, str]) -> Note:
        return Note(
            data['title'],
            data['content'],
            data.get('category', 'Nauka'),
            data.get('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

    def save_notes(self) -> None:
        with open(self.json_file, "w") as file:
            json.dump([note.save_data() for note in self.notes], file, indent=4)

    def save_note(self) -> None:
        title = self.note_title.text().strip()
        content = self.note_content.toPlainText().strip()
        category = self.note_category.currentText()

        if title and content:
            note = NoteFactory.create_note(category, title, content)
            self.notes.append(note)
            self.save_notes()
            self.note_title.clear()
            self.note_content.clear()
            self.refresh_notes_list()
            QMessageBox.information(self, "Success", "Note saved successfully!")
        else:
            QMessageBox.warning(self, "Warning", "Both title and content are required to save a note.")

    def refresh_notes_list(self) -> None:
        self.notes_list.clear()
        sorted_notes = self.sort_strategy.sort(self.notes)
        for note in sorted_notes:
            item = QListWidgetItem(f"{note.title} ({note.category}) - {note.date}")
            self.notes_list.addItem(item)

    def load_note(self, item: QListWidgetItem) -> None:
        for note in self.notes:
            if f"{note.title} ({note.category}) - {note.date}" == item.text():
                self.note_title.setText(note.title)
                self.note_content.setText(note.content)
                self.note_category.setCurrentText(note.category)
                break

class ObfuscatedNotesDecorator(NotesInterface):
    def __init__(self, notes_component: Notes, obfuscator: SimpleObfuscator):
        self._notes = notes_component
        self._obfuscator = obfuscator
        self.widget = self._notes
        # Podpinamy nasze metody do komponentu
        self._notes.save_note = self.save_note.__get__(self)
        self._notes.save_notes = self.save_notes.__get__(self)
        self._notes.load_notes = self.load_notes.__get__(self)
        # Ładujemy notatki od razu
        self.load_notes()

    def load_notes(self) -> List[Note]:
        try:
            with open(self._notes.json_file, "r") as file:
                obfuscated_notes = json.load(file)
                deobfuscated_notes = [self._deobfuscate_note(note) for note in obfuscated_notes]
                self._notes.notes = [self._notes.create_note_from_data(note) for note in deobfuscated_notes]
                self._notes.refresh_notes_list()
                return self._notes.notes
        except (FileNotFoundError, json.JSONDecodeError):
            self._notes.notes = []
            return []

    def save_notes(self) -> None:
        notes_data = [note.save_data() for note in self._notes.notes]
        obfuscated_notes = [self._obfuscate_note(note) for note in notes_data]
        with open(self._notes.json_file, "w") as file:
            json.dump(obfuscated_notes, file, indent=4)

    def save_note(self) -> None:
        title = self._notes.note_title.text().strip()
        content = self._notes.note_content.toPlainText().strip()
        category = self._notes.note_category.currentText()

        if title and content:
            note = NoteFactory.create_note(category, title, content)
            self._notes.notes.append(note)
            self.save_notes()
            self._notes.note_title.clear()
            self._notes.note_content.clear()
            self._notes.refresh_notes_list()
            QMessageBox.information(self._notes, "Success", "Note saved successfully!")
        else:
            QMessageBox.warning(self._notes, "Warning", "Both title and content are required to save a note.")

    def _obfuscate_note(self, note: Dict[str, str]) -> Dict[str, str]:
        return {
            "title": self._obfuscator.obfuscate(note["title"]),
            "content": self._obfuscator.obfuscate(note["content"]),
            "category": self._obfuscator.obfuscate(note["category"]),
            "date": self._obfuscator.obfuscate(note["date"])
        }

    def _deobfuscate_note(self, note: Dict[str, str]) -> Dict[str, str]:
        return {
            "title": self._obfuscator.deobfuscate(note["title"]),
            "content": self._obfuscator.deobfuscate(note["content"]),
            "category": self._obfuscator.deobfuscate(note["category"]),
            "date": self._obfuscator.deobfuscate(note["date"])
        }
