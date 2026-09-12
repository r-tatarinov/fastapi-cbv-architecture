# Ready-to-develop Bootstrap

Read this entire document in Bootstrap mode, after `core.md`, `modes.md`, and
`routing-infrastructure.md`. It defines implemented starter capabilities, not a tree
of future placeholders. The bootstrap rules encode the reusable architecture defined
by this skill. Generate projects from these normative rules without requiring access
to external reference projects, templates, or repositories.

Create the baseline components specified below. Add domain models, identity providers,
billing, translations, and integrations only when the current project requires them.
Do not create speculative stubs or include dependencies without a current purpose.
Explicit user requirements override the defaults here. Adapt an existing source layout
instead of creating a second one.

## Project inventory

Use Python 3.12, FastAPI, `fastapi-utils` CBV, Pydantic v2, SQLAlchemy 2 async,
asyncpg/PostgreSQL, Uvicorn, and Alembic by default. Include any runtime dependency
needed by CBV and the chosen configuration loader. Resolve compatible versions in
the target environment and include only dependencies needed by the generated project.

```text
project/
├── README.md
├── .gitignore
├── .dockerignore
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── <initial_records_migration>.py
└── src/
    ├── __init__.py
    ├── requirements.txt
    ├── run.py
    └── app/
        ├── __init__.py
        ├── main.py
        ├── config.py
        ├── app_setup/
        │   ├── __init__.py
        │   ├── auth.py
        │   ├── docs.py
        │   ├── middleware.py
        │   └── lifecycle.py
        ├── orm_sender/
        │   ├── __init__.py
        │   ├── manager_sqlalchemy.py
        │   └── utils.py
        ├── tasks/
        │   └── __init__.py
        ├── routes/
        │   ├── __init__.py
        │   ├── general_models.py
        │   ├── utils.py
        │   ├── includes_routes/
        │   │   └── __init__.py
        │   ├── base/
        │   │   ├── __init__.py
        │   │   ├── abstract_routes.py
        │   │   ├── general_routes.py
        │   │   └── mixins/
        │   │       ├── __init__.py
        │   │       └── main_router_mixin.py
        │   └── records/
        │       ├── __init__.py
        │       ├── router.py
        │       ├── base.py
        │       ├── models.py
        │       └── response_models.py
        ├── models/
        │   ├── __init__.py
        │   └── record.py
        └── model_mixins/
            ├── __init__.py
            └── record/
                ├── __init__.py
                └── data.py
```

Packages export their public objects explicitly. Keep the application package
`__init__.py` lightweight to avoid initializing the app when importing models or
migration metadata. `main.py` exposes `create_app()` and `application = create_app()`;
`src/run.py` re-exports `application` for `uvicorn src.run:application` from the project
root. Required infrastructure modules contain working behavior; empty task
registration is valid because no business background job is part of the starter.

## Application setup, ORM, and tasks

- `config.py` loads and validates environment settings once at the composition
  boundary. Include app title/version, database host/port/name/user/password,
  docs username/password, and allowed CORS origins. Use the familiar environment
  names `SQL_HOST`, `SQL_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`,
  `DOCS_DEFAULT_USERNAME`, and `DOCS_DEFAULT_PASSWORD`. Supply all required variables
  in `.env.example` and document local versus Compose database hosts. Do not put
  credentials in source or version a real `.env`.
- `ManagerSQLAlchemy` owns an instance's async engine and session factory; it is not
  a global engine instantiated as a class attribute. Export a shared SQLAlchemy
  `DeclarativeBase` from `orm_sender`. Build the database URL with SQLAlchemy's URL
  builder so passwords with special characters work. Do not open connections or
  create tables on module import.
- `create_app()` creates the manager and stores it in app state. A session dependency
  yields an `AsyncSession` from its factory with `expire_on_commit=False`, closes it
  reliably, and does not auto-commit. Routers inject the session and delegate; feature
  mutations own commit/rollback. Non-HTTP task owners use the same session factory.
- `orm_sender/utils.py` implements `get_or_create(session, model, get_args,
  create_args)` and a clone helper accepting an instance plus overrides/excluded
  columns. Both reuse the caller's session and only flush. Clone mapped non-primary-key
  scalar columns, not relations; `get_or_create` is a lookup/create convenience, not
  a concurrency-safe upsert. Unique conflicts remain the transaction owner's concern.
- `tasks/__init__.py` exports an explicit, initially empty collection of async job
  factories accepting the app and returning awaitables. Lifespan starts those jobs
  inside the running loop, keeps task handles, observes/logs failures, cancels and
  awaits jobs during shutdown, then disposes the engine even if cleanup fails.
  Business jobs own their loops and transaction boundaries. Do not create dummy jobs.
  Add schedulers, retry frameworks or workers, production-specific jobs, and periodic
  tasks only when the current project requires them.
- Use FastAPI lifespan for resource setup/cleanup. `middleware.py` configures CORS
  from settings, with no allowed cross-origin hosts by default. Allow credentials
  only with explicitly configured origins, never a credentialed wildcard.
- `auth.py` implements documentation-only HTTP Basic authentication with constant-time
  credential comparison. `docs.py` registers ReDoc at `/default/openapi` and its schema
  at `/default/openapi.json`, both authenticated and excluded from the schema itself.
  Missing or incorrect credentials return 401 with `WWW-Authenticate: Basic`. Disable
  FastAPI's default docs/redoc/openapi URLs so no unprotected schema route remains.
  Do not mistake accepting any bearer token for implementing application authentication.
- `routes/includes_routes/__init__.py` composes feature routers into an ordinary
  `APIRouter(prefix="/default")`; `routes` exports it and `create_app()` includes it.
  No automatic route discovery or multi-zone hierarchy is needed for one API group.

## Shared API contracts

`routes/general_models.py` owns `GeneralParams`, `GeneralListMeta`, a generic success
envelope, and error payload/envelope schemas. Feature models specialize these public
contracts. Do not copy domain schemas into this module.

| Query parameter | Starter contract |
| --- | --- |
| `start` | Integer, default 0, minimum 0 |
| `limit` | Integer, default 20, range 1–100 |
| `order_by` | String, default `id_asc`; allowed values defined by the feature |
| `search` | Optional string; empty means no search |
| `filter_by` | Optional string using `field:value1,value2;field2:value` |
| `is_download` | Boolean, default false; download the JSON response when true |

Expose these through a FastAPI-compatible dependency with validated concrete values
and accurate OpenAPI parameters. There is no `response_fmt` or YAML/XML support.
Framework parameter-validation errors may retain FastAPI's 422 response; feature
query errors such as an unknown ordering/filter key use the common 400 error envelope.

Implement `MainRouterMIXIN` under `routes/base/mixins/` with this public response method:

```python
get_data(data, status_code=200, meta=None, is_download=False)
```

Its output is a JSON `Response` with `{data: ..., success: ..., meta?: ...}`. Include
metadata when it is supplied, without mutating it; derive `success` from HTTP status
(`status_code < 400`). Bodyless HTTP statuses must remain bodyless. Implement this
once in `routes/utils.py`, using FastAPI-compatible JSON encoding for values such as
dates and UUIDs. Both ordinary responses and downloads use this builder; a download
adds a safe `.json` attachment filename and keeps `application/json` and the same body.
Never allow a download flag to turn an error status into 200.

Provide shared success/error helpers on `MainRouterMIXIN` delegating to `get_data`:
generic bad request (400), authentication (401), permission (403), not found (404),
and conflict (409). Errors use `{data: {error: <message>}, success: false}`. Keep safe
messages overridable by a feature and use no catalog-specific lookup or terminology.
Framework exceptions remain FastAPI/exception-handler responsibilities, as described
in `routing-infrastructure.md`.

### Collection abstraction

Use `AbstractBaseRouter` as an actual `ABC`, with `@abstractmethod` combined with
`@classmethod` or `@staticmethod` where appropriate. Declare only hooks used by the
list flow: `set_order_by(order_by, select_rel)` and
`get_data_by_response(instances, params)`. The latter is a synchronous projection of
already loaded instances; it receives no session and performs no database I/O.
Do not require create/site/default variants or empty implementations.

`GeneralBaseRouter` implements the shared collection flow and composes
`MainRouterMIXIN`. Response-only features can use `MainRouterMIXIN` directly. Preserve
these recognizable entry points:

- `get_response_by_select_rel(session, params, select_rel)` counts the filtered root
  population, retrieves a page, invokes the projection hook, and wraps the result.
- `get_instances_by_response(session, params, select_rel)` applies offset/limit and
  returns loaded ORM objects. Do not collect IDs and query the same page again.
- `get_count_by_select_rel(session, select_rel)` counts before pagination, without
  ordering. Count the same logical population as the page; the shared starter flow
  takes one row per root entity. Join-heavy features must supply a root-distinct
  statement or specialize both count and page flow, not deduplicate after pagination.
- `parse_filter_by` and `apply_filter_by` parse and apply the established scalar-filter
  syntax using explicit allowed field expressions and value converters supplied by
  the feature. Multiple values for one key are alternatives; separate keys combine
  with AND. Reject malformed segments, duplicate keys, empty values, unknown keys,
  and failed conversions with a normalized 400 response. Treat booleans explicitly
  instead of applying Python's `bool()` to nonempty strings.

The feature base builds the root statement, applies explicit search/filter/order
logic, and selects eager loaders. Common code must not guess fields such as `field`,
`menutitle`, or even the name of the feature's primary key. Unsupported supplied
search/filter/order options must not silently disappear. Sorting must be deterministic
(for example append the root primary key when ordering by a nonunique label).

Always return `meta = {"total": len(data), "counts": matching_count}`. An empty page
has `data=[]` and `total=0` but retains its actual matching count, including when
`start` lies beyond the final page. Do not bypass counting on an empty result.

## Example feature and local startup

Provide `GET /default/records/` as the small complete example. `Record` has integer
primary key `id` and required string `label` (maximum 255 characters). Define it in
`models/record.py`, inheriting a separately exported `RecordDataMixin` with `data`
and `data_by_list`, each returning `{id, label}`. The example has no relations.

`RecordsBaseRouter` inherits `GeneralBaseRouter`, searches `Record.label`, allows
filters on `id` and `label`, and supports `id_asc`, `id_desc`, `label_asc`, `label_desc`.
It projects loaded instances through `data_by_list`. `RecordsRouter` inherits that
feature base and uses `@cbv(records_router)` with a `get` method owning only HTTP
dependencies and delegation. Provide list/error schemas and response examples in
their respective feature files. Do not add fake authentication or unrelated CRUD
endpoints. The database may initially contain no records; fixtures are for validation.

Supply a working Alembic environment using the configured database URL and exported
model metadata, including import of `Record`. The initial migration creates the table
and its downgrade removes it. Migrations run as an explicit command, not on each
web-worker startup; do not replace migrations with runtime `create_all`.

Compose provides API and PostgreSQL services with a named database volume and a
database readiness check. The Docker build includes the source, migrations, and
configuration needed by the documented commands. Keep dependencies and OS packages
limited to this starter; no media, spreadsheet, storage SDK, or alternate response
format packages. Do not require a custom management script when Compose suffices.

The generated README documents copying `.env.example` to `.env`, filling credentials,
starting PostgreSQL, running `alembic upgrade head`, starting the API, and opening
authenticated documentation. Include equivalent local Uvicorn instructions and
explain changing `SQL_HOST` between a Compose service name and localhost. Explain how
to add the next feature and remove/replace the `records` example. Do not automatically
seed business data or invent additional operational endpoints.

## Acceptance checks

Check behavior, not just the existence of files. Use an isolated temporary project
when validating changes to this skill; keep generated application artifacts outside
the skill repository. For target applications, follow their test conventions.

- Install/import the declared dependencies, import `application`, enter/exit lifespan,
  and confirm the example is a registered CBV with the expected dependencies.
- Validate Compose configuration; apply the initial migration to a disposable database
  and exercise the example against it. Never run these checks against a live
  application database.
- Check the normal and empty list, `start` beyond the last page with nonzero `counts`,
  offset/limit boundaries, explicit search, typed filters, invalid filter/order input,
  and deterministic ordering. Validate emitted bodies against their Pydantic schemas
  because returning `Response` bypasses FastAPI's `response_model` validation.
- Compare downloaded JSON with the ordinary envelope, including attachment headers
  and status preservation; check expected error helpers and bodyless responses.
- Verify both docs endpoints reject missing/wrong credentials and accept correct
  credentials; ensure the default unprotected documentation routes are absent.
- Exercise an empty task list, a running task, and a failing task: failures are observed,
  shutdown cancels/awaits handles, and the engine is disposed. Check ORM helpers reuse
  the caller's session without committing and projections cause no SQL.
- Verify a new feature can reuse the implemented base without unrelated abstract
  stubs, domain imports, or additional response/query infrastructure. Preserve the
  core thin-router, eager-loading, and transaction-ownership invariants.

Report checks not run due to missing dependencies, Docker, or PostgreSQL separately
from successful static checks. A documentation-only review does not establish that
the generated project starts or that database behavior is correct.
