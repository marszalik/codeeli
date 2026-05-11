# General Architecture

This document describes the current layout of the application and the conventions to follow as the project evolves.

## Stack

* FastAPI handles HTTP routing and the API
* Mako renders HTML views on the server side
* SQLite stores application settings and the manual ordering of elements

## Core principle

The most important rule: **the project is organized by domain, not by layer**.
Code related to a single functional area is kept together:

* routing
* domain logic
* data schemas
* Mako views specific to that domain

We do not use global directories like:

* `routers/`
* `services/`
* `templates/`

for the whole application.

## Directory structure

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

Code shared across the whole application.
Contains:

* `config.py` – settings and runtime paths
* `templates.py` – Mako configuration (lookup, rendering)
* `views/` – shared views (e.g. `base.mako`)
* `static/` – shared assets

This place is for framework and shared concerns, **not for business logic**.

## Domain structure

Every domain should contain:

* `router.py` – mapping HTTP → domain operations
* `service.py` – business logic and data operations
* `repository.py` – data access (e.g. SQLite)
* `schemas.py` – data models (request/response)
* `views/` – Mako views specific to the domain
* `static/` – CSS/JS specific to the domain

## Views (Mako)

Views are scoped to domains.

### Rules:

* domain-specific view → `app/domains/<domain>/views/`
* shared view → `app/domains/core/views/`

### Why:

* easier to reason about a feature
* routing + view + logic stay close together
* better AI collaboration
* easier to delete and grow domains
* no "flat list of templates"

## Routing

Each domain owns its own `router.py`.
The router:

* should be **thin**
* maps HTTP → domain operations
* contains no business logic or persistence

If a handler:

* operates on files
* runs SQL
* validates business rules

→ that logic belongs in `service.py`.

## Frontend

* domain-scoped static assets live inside the domain
* shared assets move to `core/`

## Development conventions

When adding a new feature:

1. Pick the domain
2. If the feature is local → keep everything in the domain
3. If it is shared → only then move it to `core/`

### Rules:

* do not put business logic into Mako
* do not put heavy logic into routers
* do not mix SQL with the HTTP layer

### Adding a new screen:

1. pick the domain
2. add the view under that domain's `views/`
3. wire it through that domain's router

## What to avoid

* a global `templates/` for every view
* shoving all logic into `app.js`
* direct SQLite access from routers
* mixing auth logic with other domains
* creating a `utils.py` with no clear responsibility

## Content

* all content is injected into Mako via variables
* content is stored under the `content/` directory
* format: **markdown only**

### Structure:

* identifiers mirror file paths
* repeated content → separate files

Example:

```
content/  news/    news1.md    news2.md
```
