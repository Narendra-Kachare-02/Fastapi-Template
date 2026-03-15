# ArjanCodes–Style Clean Code Checklist

Based on Arjan's blog posts, videos, and guides, we distilled the following **strict rules** for organizing and naming code. These checkpoints reflect Arjan's style for maintainable, scalable Python projects:

- **Use a clear package/module structure.** Put all application code in a `src/` directory (or main package) and separate subpackages by domain or layer (e.g. `services/`, `repositories/`, `models/`, `utils/`)【19†L1-L4】【27†L153-L160】. Avoid "spaghetti files" – group related code into packages (each with its own `__init__.py`).  
- **Domain-based naming.** Name files by *what they contain*, not generic names. Prefer `snake_case` (PEP8) for filenames and modules. Inside a folder the name is the noun only (folder already gives the layer): use a concrete domain name, not a generic one – e.g. `order.py` in `services/`, `order.py` in `repositories/`, `file.py` in `utils/`【3†L119-L124】【27†L153-L160】.  
- **Consistent naming conventions.** Be consistent across the project. Stick to snake_case for modules/functions and PascalCase for classes. Avoid mixing styles. Each name should immediately suggest its role (e.g. `client.py` for client-related logic)【3†L119-L124】.  
- **One responsibility per module/class.** Each file or class should have a single, focused responsibility (the "Single Responsibility" principle). Large classes should be refactored into smaller components【27†L153-L160】. Break down monolithic classes or scripts into units (e.g. split validation, data access, and business logic into separate modules). This makes code easier to understand and test【27†L153-L160】【12†L69-L77】.  
- **Thin entry-point files (Controllers).** Top-level API/routes files (e.g. FastAPI routers or main scripts) should be minimal: validate input, call the service layer, and return responses. Put all heavy logic, file I/O, DB access, etc. into services or domain modules, not in the route handlers. This clean "controller" pattern improves readability and testing (Arjan emphasizes keeping views thin).  
- **Use a service/repository pattern.** Implement a clear separation between business logic (services) and data access (repositories). For example, `order.py` in services handles use-case logic, and `order.py` in repositories handles DB or file I/O. Call external systems (databases, APIs) only from isolated client or repository modules【27†L153-L160】【33†L1-L4】.  
- **Dependency injection and configuration.** Pass dependencies (config, database connections, HTTP clients) into services rather than hard-coding them. Arjan recommends using Python DI (or FastAPI's built-in DI) to keep components loosely coupled【27†L183-L191】【33†L1-L4】. Manage configuration centrally (e.g. environment variables in a `.env` file and a `config.py` module). Include a `.python-version` file or similar to pin the Python version【33†L1-L4】.  
- **Folder and file structure (example):** Adopt a standard layout such as: 
  ```
  my_project/
  ├── src/
  │   ├── my_project/           # main package
  │   │   ├── __init__.py
  │   │   ├── config.py        # global settings
  │   │   ├── main.py          # entry point (e.g. FastAPI app)
  │   │   ├── api/             # route definitions (versioned: api/v1/endpoints/, api/v2/endpoints/)
  │   │   │   ├── __init__.py
  │   │   │   └── v1/
  │   │   │       ├── __init__.py   # prefix /api/v1/endpoints
  │   │   │       └── endpoints/
  │   │   │           ├── __init__.py
  │   │   │           ├── health.py
  │   │   │           └── orders.py
  │   │   ├── services/        # business logic
  │   │   │   └── order.py
  │   │   ├── repositories/    # data access layer
  │   │   │   └── order.py
  │   │   ├── models/          # Pydantic or domain models
  │   │   │   └── order.py
  │   │   └── utils/           # helper modules (e.g. file.py)
  │   │       └── file.py
  │   └── tests/               # separate test suite
  │       └── test_order.py
  ├── docs/                    # documentation (README, design docs)
  │   └── README.md
  ├── .env                     # environment config file
  ├── .gitignore
  ├── pyproject.toml           # project metadata and dependencies
  └── LICENSE.md               # license file (Arjan: "non-negotiable")【21†L153-L160】
  ```  
  This follows Arjan's advice to isolate source code in `src/`, keep tests and docs separate, and include standard files【19†L1-L4】【21†L92-L100】【21†L109-L118】.  
- **Documentation first.** Write a clear `README.md` describing the project's purpose, setup, and examples【21†L109-L113】. Keep docs (like design notes or wiki) in a `docs/` folder. Good documentation is part of a clean codebase.  
- **Version control essentials.** Always include a `.gitignore` to exclude virtual environments, secrets, cache, etc.【21†L128-L136】. Use `pyproject.toml` for dependency management (PEP 518 standard)【21†L139-L147】. Include a `LICENSE` file to clarify usage terms【21†L153-L160】.  
- **Logging and monitoring.** Centralize logging (e.g. configure a logger in one module). Arjan stresses having "centralized logging" for debugging large apps【33†L1-L4】. Don't scatter logging calls everywhere; use a common logger configuration.  
- **Avoid premature abstraction.** Use design patterns and abstractions only when they solve a concrete problem【12†L69-L77】【12†L99-L107】. Arjan warns against "overengineering": don't apply patterns just for the sake of it. Start simple, and refactor only when needed.  
- **Module vs Class.** If a set of functions don't share state, prefer a module with functions over a class. Group related functions into packages by feature or service【27†L218-L225】.  
- **Code readability.** Emphasize type hints, clear naming, and "an intuitive interface" for your APIs and classes【27†L167-L176】. Write code that reads easily – Arjan often says "code is read more than written." Aim for code that describes itself, with consistent conventions throughout.  

Following these guidelines ensures your project is **well-organized, maintainable, and scalable** in the ArjanCodes style. For example, Arjan's "blueprint" uses a flat folder hierarchy, domain-based modules, and dedicated config and docs folders【33†L1-L4】【19†L1-L4】. By naming files after their domain (service, repository, etc.) and splitting concerns, you make code easier to navigate and explain – exactly as Arjan recommends【3†L119-L124】【27†L153-L160】.

**API versioning (this project):** Endpoints live under `api/v1/endpoints/` (and later `api/v2/endpoints/`). In the structure above, `api/v1/endpoints/` holds route handlers (e.g. `health.py`, `orders.py`); add new endpoints there and register them in `app/api/v1/__init__.py`.

**Sources:** ArjanCodes official blog and newsletter (see "Best Practices for Python Code Structuring" and "Efficient Python Project Setup"【3†L119-L124】【21†L128-L136】【21†L139-L147】), Arjan's design patterns and architecture posts【12†L69-L77】【27†L153-L160】, and his project blueprint guides【19†L1-L4】【33†L1-L4】. These informed each rule above.
