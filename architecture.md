# General Architecture

Ten dokument opisuje aktualny układ aplikacji oraz konwencje, których należy się trzymać przy dalszym rozwoju projektu.

## Stack

* FastAPI odpowiada za routing HTTP i API
* Mako renderuje widoki HTML po stronie serwera
* SQLite przechowuje ustawienia aplikacji oraz manualny order elementów

## Główna zasada

Najważniejsza zasada: **projekt jest organizowany domenowo, a nie warstwowo**.
Kod związany z jednym obszarem funkcjonalnym trzymamy razem:

* routing
* logika domenowa
* schematy danych
* widoki Mako specyficzne dla tej domeny

Nie używamy globalnych katalogów typu:

* `routers/`
* `services/`
* `templates/`

dla całej aplikacji.

## Struktura katalogów

```
app/
  domains/
    core/
      config.py
      templates.py
      views/
        base.mako
        example_common_view.mako
      static/
        core.css
        core.js

    example_domain/
      router.py
      service.py
      repository.py
      schemas.py
      views/
        some_view.mako
      static/
        example_domain.css
        example_domain.js

    preferences/
      repository.py
      schemas.py
      service.py

  content/
    main/
      header.md
    preferences/
      greeter.md
```

## app/domains/core

Kod wspólny dla całej aplikacji.
Zawiera:

* `config.py` – ustawienia i ścieżki runtime
* `templates.py` – konfiguracja Mako (lookup, renderowanie)
* `views/` – widoki współdzielone (np. `base.mako`)
* `static/` – zasoby współdzielone

To miejsce jest dla rzeczy frameworkowych i współdzielonych, **nie dla logiki biznesowej**.

## Struktura domeny

Każda domena powinna zawierać:

* `router.py` – mapowanie HTTP → operacje domenowe
* `service.py` – logika biznesowa i operacje na danych
* `repository.py` – dostęp do danych (np. SQLite)
* `schemas.py` – modele danych (request/response)
* `views/` – widoki Mako specyficzne dla domeny
* `static/` – CSS/JS specyficzne dla domeny

## Widoki (Mako)

Widoki są przypisane do domen.

### Reguły:

* widok specyficzny → `app/domains/<domain>/views/`
* widok współdzielony → `app/domains/core/views/`

### Dlaczego:

* łatwiejsze zrozumienie feature
* routing + widok + logika są blisko siebie
* lepsza współpraca z AI
* łatwiejsze usuwanie i rozwijanie domen
* brak „płaskiej listy templatek”

## Routing

Każda domena ma własny `router.py`.
Router:

* powinien być **cienki**
* mapuje HTTP → operacje domenowe
* nie zawiera logiki biznesowej ani persistence

Jeśli handler:

* operuje na plikach
* robi SQL
* waliduje reguły biznesowe

→ logika trafia do `service.py`

## Frontend

* statics domenowe trzymamy w domenach
* rzeczy współdzielone przenosimy do `core/`

## Konwencje rozwoju

Przy dodawaniu nowego feature:

1. Określ domenę
2. Jeśli feature jest lokalny → trzymaj wszystko w domenie
3. Jeśli współdzielony → dopiero wtedy przenieś do `core/`

### Zasady:

* nie wkładaj logiki biznesowej do Mako
* nie wkładaj ciężkiej logiki do routerów
* nie mieszaj SQL z warstwą HTTP

### Dodanie nowego ekranu:

1. wybierz domenę
2. dodaj widok w `views/` tej domeny
3. podepnij przez router tej domeny

## Czego unikać

* globalnego `templates/` dla wszystkich widoków
* przerzucania całej logiki do `app.js`
* bezpośredniego dostępu do SQLite z routerów
* mieszania logiki auth z innymi domenami
* tworzenia `utils.py` bez jasnej odpowiedzialności

## Content (treści)

* wszystkie treści są wstrzykiwane do Mako przez zmienne
* treści są przechowywane w katalogu `content/`
* format: **wyłącznie markdown**

### Struktura:

* identyfikatory odpowiadają ścieżkom plików
* treści powtarzalne → osobne pliki

Przykład:

```
content/  news/    news1.md    news2.md
```