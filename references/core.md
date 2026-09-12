# Core Architecture

This document defines the reusable architecture. Bootstrap obtains its concrete files
from the bundled assets; Extend first follows the target project's compatible active
conventions.

## Project shape

```text
src/
├── run.py                         # re-export application
└── app/
    ├── __init__.py                # create_app and application
    ├── config.py                  # environment constants
    ├── orm_sender/
    │   ├── manager_sqlalchemy.py  # ManagerSQLAlchemy only
    │   └── utils.py               # ORM helper functions
    ├── routes/
    │   ├── mixins.py              # shared response/router mixins
    │   ├── general_models.py      # shared request/response contracts
    │   ├── utils.py               # response decorator/utilities
    │   ├── base/
    │   │   ├── abstract_routes.py
    │   │   └── general_routes.py
    │   └── <feature>/
    │       ├── __init__.py
    │       ├── base.py
    │       ├── models.py
    │       ├── router.py
    │       └── response_models.py # optional OpenAPI metadata/examples
    ├── models/
    │   ├── base.py
    │   └── <entity>.py
    └── models_mixins_data_responses/
        └── <entity>.py
```

Do not rename these established boundaries to `model_mixins/`, move
`MainRouterMIXIN` under `routes/base/mixins/`, move `Base` into the ORM manager, or
introduce a separate `main.py` during Bootstrap.

## Application and ORM

- `src/app/__init__.py` owns `create_app()` and `application`; `src/run.py` only
  re-exports `application`.
- `config.py` exposes environment-backed constants. Bootstrap includes only the
  database constants required by `ManagerSQLAlchemy`.
- `ManagerSQLAlchemy` owns the class-level async engine. Consumers inherit it and open
  `AsyncSession(self.engine, autoflush=False, expire_on_commit=False)` at the HTTP,
  task, or orchestration boundary that owns the session.
- Do not add constructor injection, an app-state database manager, a session factory,
  URL builder, session dependency, lifecycle disposal method, or declarative base to
  `manager_sqlalchemy.py` unless the target project has already adopted that API.
- `models/base.py` owns SQLAlchemy `Base`. Each mapped model occupies one file.
- ORM helper functions remain module functions in `orm_sender/utils.py`; do not fold
  them into the manager class or change their established return shapes incidentally.

One atomic mutation still uses one session and one transaction owner. Nested helpers
receive that session, may flush, and do not commit the caller's transaction.

## Feature boundary

A feature is a cohesive API capability. Its router owns endpoint decorators, HTTP
parameters, dependencies, authentication/session wiring, response metadata, and
delegation. Its base owns reusable queries, mutations, business validation, result
construction, and feature behavior.

```text
APIRouter
    ↓
@cbv(feature_router)
    ↓
FeatureRouter(FeatureBase)
```

- Use FastAPI `APIRouter` and `fastapi_utils.cbv.cbv`.
- The CBV class inherits its feature-local base.
- Endpoint method names match the decorator verb: `get`, `post`, `put`, `patch`, or
  `delete`.
- Call inherited behavior through `self`, `cls`, or correct `super()` dispatch.
- Do not create service/repository layers without a distinct current responsibility.

## ORM response ownership

An API-facing ORM entity has a corresponding flat module in
`models_mixins_data_responses/`; the mapped model inherits that response mixin.

```text
models/<entity>.py
models_mixins_data_responses/<entity>.py
```

Representations of one entity (`data`, `data_by_list`, or another established `data*`
variant) belong in its response mixin. Composite or computed results belong in the
feature base. HTTP envelopes belong in routing infrastructure.

Derive eager loaders from every relation and nested representation read by the chosen
builder. Serialization of a fully loaded object must not trigger SQL.

## Class and module organization

- Keep the symbol family of a known module intact. A file that owns a class must not
  accumulate unrelated factories, dependencies, or base declarations.
- In new or substantially changed classes, group ordinary instance methods first,
  then `@classmethod` methods, then `@staticmethod` methods.
- Remove irrelevant source capabilities as complete imports/methods/blocks. Do not
  rewrite retained behavior into a different abstraction while calling it a cleanup.
- Treat a working historical deviation as context, not automatic permission to mass
  refactor it.
