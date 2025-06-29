## Spis przypadków testowych

### 1. UserService

* register\_user: sukces rejestracji - instancja usera, commit
* register\_user: brak pól - ValueError "Wszystkie pola są wymagane"
* register\_user: duplikat użytkownika - ValueError "Użytkownik o podanej nazwie lub emailu już istnieje"
* register\_user: błąd zapisu do bazy - rollback i ValueError o zapisie
* authenticate\_user: poprawne dane - zwraca usera
* authenticate\_user: złe hasło lub brak usera - zwraca None
* get\_user\_by\_id: istniejący ID - zwraca usera; nieistniejący - None
* get\_all\_users: zwraca listę userów
* delete\_user: istniejący user - usuń i zwróć True; nieistniejący - False

### 2. TaskService

* create\_task: sukces - nowy Task, commit
* create\_task: brak pól - ValueError o brakujących polach
* create\_task: niepoprawny format daty - ValueError o formacie
* create\_task: przeszły deadline - ValueError o przyszłości
* create\_task: brak priorytetu - default Medium
* create\_task: błąd commit - rollback i wyjątek
* get\_tasks\_by\_project: zwraca listę zadań
* get\_task\_by\_id: zwraca Task lub None
* update\_task: brak taska - None
* update\_task: sukces - aktualizuje pola, commit
* update\_task: zły deadline - ValueError
* delete\_task: usuń istniejący - True; nieistniejący - False

### 3. StatusManager

* change\_status: sukces - zmiana statusu, zapis historii, 2× commit
* change\_status: brak taska - ValueError
* change\_status: błąd update lub historii - rollback i wyjątek
* get\_history\_for\_task: zwraca listę historii

### 4. StatisticsGenerator

* task\_count\_by\_status: \[] zwraca {}
* task\_count\_by\_status: lista statusów zwraca mapę status→liczba
* generate\_global\_stats: zwraca total\_tasks, total\_projects, status\_counts

### 5. ProjectService

* create\_project: sukces - nowy Project, commit
* create\_project: brak pól - ValueError
* create\_project: domyślna pusta opis - description = ''
* create\_project: błąd commit - rollback i wyjątek
* get\_projects\_by\_owner: lista projektów
* get\_project\_by\_id: Project lub None
* update\_project: brak projektu - None; sukces - commit
* delete\_project: usuń istniejący - True; nieistniejący - False

### 6. PriorityHandler

* normalize\_priority: różne warianty tekstu mapowane na High/Medium/Low
* is\_valid\_priority: tylko Low/Medium/High → True
* compare\_priority: porównanie priorytetów -1/0/1

### 7. NotificationService

* log\_notification: wypisuje log z timestampem, opcjonalne details
* send\_task\_assignment\_notification: log\_notification z "task\_assigned"
* send\_status\_change\_notification: log\_notification z "status\_changed"
* send\_comment\_notification: log\_notification z "new\_comment"

### 8. DeadlineValidator

* is\_valid\_deadline: None → False
* is\_valid\_deadline: nie-datetime → ValueError
* is\_valid\_deadline: data < teraz → False; data >= teraz → True

### 9. CSVExporter

* export\_tasks\_for\_project: brak projektu → None
* export\_tasks\_for\_project: brak zadań → CSV z nagłówkiem i pustą sekcją
* export\_tasks\_for\_project: zadania → CSV z danymi

### 10. CommentService

* add\_comment: sukces - nowy Comment, commit
* add\_comment: brak danych - ValueError
* add\_comment: błąd commit - rollback i wyjątek
* get\_comments: zwraca listę komentarzy
* delete\_comment: brak komentarza lub nieautor - False; sukces - True
* get\_comment\_by\_id: Comment lub None
