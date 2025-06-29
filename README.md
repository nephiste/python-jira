## Python JIRA – System zarządzania projektami i zadaniami

Aplikacja webowa inspirowana JIRA, napisana we Flasku z bazą danych SQLite. Umożliwia zarządzanie użytkownikami, projektami, zadaniami, komentarzami oraz eksportem danych. Gotowa do uruchomienia lokalnie lub przez Docker.

## Technologie

- Python 3.9
- Flask + SQLAlchemy
- SQLite
- Bootstrap 5 + JavaScrip
- Docker & Docker Compose
- Pytest + Mock (testy jednostkowe)

---

## Instrukcja uruchomienia z Docker:

W katalogu głównym projektu uruchom:

```bash
docker-compose build
docker-compose up
```

Aplikacja będzie dostępna pod adresem:
[http://localhost:5000](http://localhost:5000)

---

##  Instrukcja uruchomienia lokalnego

1. **Klonuj repozytorium**:

```bash
git clone https://github.com/twoje-repo/python-jira.git
cd python-jira
```

2. **Utwórz i aktywuj środowisko wirtualne**:

```bash
python -m venv venv
venv\Scripts\activate         # Windows
# lub
source venv/bin/activate     # macOS/Linux
```

3. **Zainstaluj zależności**:

```bash
pip install -r requirements.txt
```

4. **Zainicjalizuj bazę danych**:

```bash
flask db init
flask db migrate -m "initial"
flask db upgrade
```

5. **Uruchom aplikację**:

```bash
flask run
```

Aplikacja będzie dostępna pod adresem:
[http://localhost:5000](http://localhost:5000)

---

## Testy

Aby uruchomić testy i sprawdzić pokrycie:

```bash
pytest
coverage run -m pytest
coverage report
coverage html # wygeneruj plik html
```
