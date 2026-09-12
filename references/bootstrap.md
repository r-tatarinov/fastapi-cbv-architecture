# Fixed Bootstrap

Bootstrap is a deterministic copy operation, not an invitation to redesign a new
FastAPI project. Use the bundled scaffold:

```bash
python scripts/bootstrap_project.py TARGET [--project-name NAME] [--port PORT]
```

The curated source files are pinned to tracked reference revision `1d48a53`; this
provenance note belongs to the skill and is not copied into generated projects.

`TARGET` may already exist, but none of the scaffold paths may conflict. The script
checks all conflicts before writing anything. It derives the project title from the
target directory name when `--project-name` is omitted and uses port `2309` by
default.

## Generated inventory

```text
project/
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── src/
    ├── .env.example
    ├── __init__.py
    ├── requirements.txt
    ├── run.py
    └── app/
        ├── __init__.py
        ├── config.py
        ├── i18n/
        │   ├── __init__.py
        │   └── context.py
        ├── models/
        │   ├── __init__.py
        │   └── base.py
        ├── models_mixins_data_responses/
        │   └── __init__.py
        ├── orm_sender/
        │   ├── __init__.py
        │   ├── manager_sqlalchemy.py
        │   └── utils.py
        └── routes/
            ├── __init__.py
            ├── general_models.py
            ├── mixins.py
            ├── utils.py
            └── base/
                ├── __init__.py
                ├── abstract_routes.py
                └── general_routes.py
```

This inventory is exhaustive. Bootstrap does not generate `main.py`, Alembic,
migrations, `pyproject.toml`, dev requirements, tests, tasks, `app_setup`, an example
feature, or an API endpoint.

## Source-fidelity rules

- `src/app/orm_sender/manager_sqlalchemy.py` contains only
  `ManagerSQLAlchemy`, whose `engine` is the class attribute used by inheritors.
- `src/app/models/base.py` owns `Base`; do not move it into the ORM manager.
- ORM helper functions remain in `orm_sender/utils.py` and keep their established
  return values and signatures.
- Shared response behavior remains in `routes/mixins.py`; collection orchestration
  remains in `routes/base/general_routes.py`.
- Shared routing code contains no concrete entity fields, relation-specific hooks, or
  feature-specific errors. Features add those contracts during Extend.
- Entity response mixins use the flat `models_mixins_data_responses/` package.
- Only the project title and Docker port are scaffold substitutions. The Docker
  service name is the generic `api`.
- The generated tree must contain no reference-project or prior generated-project
  names.

## Environment and Docker

The scaffold creates `src/.env.example`, never a real `.env`. Copy it to `src/.env`
and replace its placeholder database values before starting Compose. The Compose file
defines only the API service and expects the configured PostgreSQL host to exist; do
not add a database service implicitly.

The Dockerfile may install dependencies inside its image. This does not authorize
creating `.venv`, installing packages on the host, or running Docker automatically.
Run Docker commands only when they are part of the user's requested work or validation.

## Acceptance checks

- Run `python scripts/validate_bootstrap.py` and the skill validator.
- Generate into a temporary empty directory and confirm the exact inventory.
- Confirm a second generation refuses conflicts without partially writing.
- Confirm no `.venv`, local-install command, unexpected symbol, or project/feature
  identity is generated.
- Run `docker compose config` with a temporary `src/.env` when Docker is available.
- Build/import inside Docker only when environment and authorization permit it; report
  unavailable external checks separately.
