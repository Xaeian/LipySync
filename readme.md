## 📖 Lipy`Sync`

Ten programik **eliminuje problem rozproszenia bibliotek**, poprzez synchronizację 🔄 wybranych plików oraz całych katalogów, które są porozrzucane po różnych projektach na kompie _(lokalnie)_. Dzięki temu unikasz chaosu i ręcznego kopiowania plików.

Pozornie centralizacja bibliotek wydaje się świetnym pomysłem. Ułatwia organizację pracy i pozwala uniknąć duplikowania kodu. W praktyce pojawiają się jednak pewne komplikacje:

- Nie zawsze chcemy aktualizować bibliotekę w projekcie, którego dalej nie rozwijamy, ale nadal musi on działać.  
- Niektóre biblioteki muszą być częścią repozytorium. Kiedy oddajemy/zamykamy projekt, chcemy, aby wszystko było w jednym miejscu, bez konieczności pobierania dodatkowych zależności z zewnętrznych źródeł.
- Lepiej, gdy wszystkie zasoby są w katalogu projektu. Upraszcza to konfigurację (Makefile, CMake), eliminuje problemy ze ścieżkami i wersjami bibliotek oraz poprawia integrację z IDE.

To rozwiązanie sprawdzi się idealnie, jeśli prowadzisz wiele mniejszych projektów i zależy Ci na sprawnym zarządzaniu bibliotekami _(kodem, który pojawia się w wielu projektach)_. Jeśli często wprowadzasz zmiany, chcesz uniknąć bałaganu w kodzie, ale jednocześnie nie masz czasu, by poświęcać godziny na porządkowanie zależności, to narzędzie jest dla Ciebie! Program jest banalnie prosty. Liczy się wydajna i skuteczna praca, bez zbędnej biurokracji. Społeczność open source może robić swoje, ale tutaj priorytetem jest zadowolony klient i dobrze działający projekt zrobiony ⚡**szybko** i 👍**jako tako**.

### 🧐 Problemy!

- ❌ **Możliwe przypadkowe nadpisania**: jeśli edytujesz dwie wersje biblioteki jednocześnie.
- ✅ Unikaj tego, ale jeśli się zdarzy, każda nadpisana wersja jest zapisywana jako kopia zapasowa z datą, więc zawsze możesz odzyskać zmiany.
- ❌ **Brak izolacji środowiska**: różne projekty mogą wymagać różnych wersji tej samej biblioteki.
- ✅ To nie problem! wystarczy utworzyć osobne wpisy dla różnych wersji, dzięki czemu synchronizacja będzie niezależna. Możesz też zakomentować wpisy dla bibliotek, które nie powinny być już aktualizowane.
- ❌ **Dublowanie kodu na repozytorium**: zamiast jednej kopii biblioteki, masz ich kilka w różnych projektach.
- ✅ I tak ma być! Każdy klient powinien mieć swoją wersję biblioteki, bez zależności od innych repozytoriów. Pełna kontrola, zero niepotrzebnych komplikacji.

### 🤔 Alternatywy?

Oczywiście można podejść do tego bardziej profesjonalnie, poprzez:

- Wersjonowanie bibliotek jako osobne projekty/repozytoria i ich aktualizację w razie potrzeby.
- Korzystanie z Git **Submodules**, co umożliwia śledzenie wersji biblioteki w repozytorium.
- Zewnętrzne menedżery pakietów _(`pip`, `npm`, `cargo`)_, które ułatwiają zarządzanie zależnościami.

Jeśli któreś z naszych bibliotek doczekają się stabilnej wersji, któej nie zmieniamy chaotycznie co projekt oraz będą wystarczjąco fajne dobrze jest przmyśleć jendo z powyższych rozwiązań

### ⚙️ Config 

Plik **`sync.json`** definiuje konfigurację synchronizacji plików i folderów bibliotecznych. Każdy obiekt w tabeli określa nazwę `name` biblioteki, pole `file` typu `true`/`false` określającej czy chodzi o plik czy katalog oraz listę ścieżek `paths`, które podlegają synchronizacji. Dodatkowo, ścieżki mogą być zapisane w skróconej formie przy użyciu pliku **`dict.ini`**, w którym definiowane są aliasy dla często powtarzających się lokalizacji. W ścieżkach w `sync.json` można odwoływać się do tych aliasów za pomocą notacji `{key}`. Jeżeli w ścieżce znajduje się znak `#` na początku, to jest ona traktowana jako zakomentowana i nie będzie brana pod uwagę w synchronizacji.

W przypadku plików możemy dodać pole `whiteList`, które umożliwi synchronizację tylko wskazanych plików, lub `blackList`, które wykluczy określone pliki. Natomiast przy synchronizacji katalogów nazwy plików muszą być identyczne!

#### Example

W przykładzie synchronizowane są dwa pliki i jeden katalog.
Z pliku `sync.json` trzeba usunąć komentarze⚠️
Wywołanie programu z flagą `-e`, `--example`, spowoduje stworzenie plików z przykładu lokalnie.

Plik `dict.ini`

```ini
web = C:/Users/Me/Projects/WebPage/backend # Ścieżka do katalogu backendu projektu internetowego
staff = C:/Users/Me/Desktop/MyStaff/test # Katalog użytkownika, zawierający różne testy
work = C:/Users/Me/Work/Drivers/repos # Główna ścieżka robocza dla repozytoriów
```

Plik `sync.json`

```json
[
  {
    "name": "serial_port.c",
    "file": true, // Wpis odnosi się do pliku 
    "paths": [
      "{staff}/serial.c", // Pełna ścieżka: "C:/Users/Me/Desktop/MyStaff/test/serial.c" 
      "{work}/PLC/{name}" // Nazwa pliku: "serial_port.c" 
    ]
  },
  {
    "name": "utils", // Wpis odnosi się do pliku. Domyślnie: "file": true 
    "paths": [
      "{web}/lib/{name}",
      "#{staff}/python/{name}.py", // Plik wyłączony z synchronizacji 
      "{work}/PLC/misc.py"
    ]
  },
  {
    "name": "protobuf",
    "file": false, // Wpis odnosi się do katalogu 
    "paths": [
      "{web}/proto/",
      "{staff}/{name}/" // Nazwa katalogu: "protobuf" 
    ]
  }
]
```

### 🚀 Use

Użycie jest banalnie proste. Wystarczy uruchomić program, który wygeneruje raport:

```bash
py main.py  # gdy używamy nieskompilowanej wersji z repozytorium  
./libpysync.exe  # gdy używamy skompilowanej aplikacji z wydania (release)  
libpysync  # gdy dodamy ją do ścieżki systemowej  
```

Aby zsynchronizować _(czyli zaktualizować starsze wersje bibliotek)_, wystarczy ponownie uruchomić program z flagą `-u`, `--update`:

```bash
py main.py --update  
./libpysync.exe -u  
libpysync -u  
```
