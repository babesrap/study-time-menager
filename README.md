
# Opis projektu
ClariSpace to kompleksowa aplikacja do zarządzania produktywnością, łącząca timer skupienia , kalendarz zadań oraz bezpieczny system notatek w jednym intuicyjnym interfejsie. Aplikacja została zaprojektowana z wykorzystaniem nowoczesnych wzorców projektowych.

## Główne Funkcje
**Focus Timer**

- Timer typu Pomodoro do efektywnej pracy
- Wybór różnych aktywności (Czytanie, Kodowanie, Nauka, Relaks)
- Predefiniowane przyciski czasowe (1, 5, 10, 15, 30 minut)
- System punktów motywacyjnych
- Statystyki czasu skupienia z wizualizacją w formie wykresu kołowego

**ToDoCalendar**

- Zarządzanie zadaniami z widokiem kalendarza
- Oznaczanie zadań jako ukończonych
- Automatyczna synchronizacja z Google Calendar
- Organizacja zadań według dat

**Notes**

- Bezpieczny system notatek z kategoryzacją
- Szyfrowanie zawartości notatek (wzorzec Dekorator)
- Sortowanie notatek według daty, tytułu lub kategorii (wzorzec Strategia)
- Kategorie: Nauka, Praca, Kodowanie, Zadania

## Wzorce projektowe

- **Decorator Pattern** - dynamiczne rozszerzanie funkcjonalności notatek o szyfrowanie
- **Strategy Pattern** - różne strategie sortowania notatek
- **State Pattern** - zarządzanie stanami timera skupienia
- **Adapter Pattern**  - dostosowanie interfejsu Google Calendar API do potrzeb aplikacji
- **Factory Pattern** - tworzenie obiektów notatek

## Instalcaja
```
# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie aplikacji
python main.py
```



