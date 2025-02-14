# Auth REST API Example

Provides a simple sample implementation of authenticated requests using an expirable JWT Token

Project is built using:
- `FastAPI`
- `SQLModel`
- `DuckDB` (in-process OLAP dbms)

## Install & Run

Project's built using `uv`

Check the required Python version in `.python-version`. Install this version if needed with:
```zsh
uv python install 3.13
```

Create a `venv` by doing:

```zsh
uv venv --python 3.13
```

Install the package with:
```zsh
make build
```

Run the project by executing
```zsh
make run
```
---

Check the API docs at http://localhost:8000/docs

---
