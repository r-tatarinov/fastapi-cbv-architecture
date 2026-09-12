# Operating Modes

Select one mode and apply the invariants from [core.md](core.md). When the work touches
shared responses, errors, query parameters, or list behavior, also apply
[routing-infrastructure.md](routing-infrastructure.md).

## Bootstrap

Use for a new or minimal project.

1. Determine the package layout, application entrypoint, and existing infrastructure.
2. Create the baseline architectural package boundaries from `core.md`, not merely
   the minimum files required to import or start FastAPI.
3. Construct the FastAPI application in `main.py`; it may have no routes.
4. If there is a real first feature, apply the feature structure from `core.md` and
   register its `APIRouter` at the application composition boundary.
5. Add a shared response, error, or collection-query implementation only when a
   concrete feature needs it as an application-wide contract. The
   `routes/base/mixins/` package boundary exists before those implementations.
6. Add persistence or integrations only when the use case requires them.
7. Do not create placeholder layers, formats, modules, or abstract hooks.

### Architectural boundaries versus implementations

Create every package in the normative Bootstrap tree in `core.md`. Those boundaries
are mandatory for a new architecture Bootstrap and may exist before the first
business feature or entity. This is the deliberate exception to the rule against
speculative layers: the packages encode the architecture, while concrete contents
remain on demand.

Do not create the following until a concrete responsibility requires them:

- `routes/<feature>/` or feature-specific Pydantic schemas;
- `models/<entity>.py`, ORM entities, or persistence infrastructure;
- `model_mixins/<entity>/` or entity projections;
- `database/` or `integrations/`;
- shared response/error implementations or list, search, filter, pagination, and
  ordering implementations inside `routes/base/`;
- separate route-registration modules or managers.

`routes/base/` is always present as the shared routing boundary, and
`routes/base/mixins/` is always present as its reusable HTTP/API behavior boundary.
This skill defines their responsibilities but no mandatory concrete implementation
names for an application with no endpoints. Therefore, a boundary containing only
`__init__.py` is the correct empty-project state. Do not populate it with
`registration.py`, `registry.py`, `router_manager.py`, placeholder response builders,
placeholder error helpers, fake base classes, or empty abstractions.

### Router registration

Do not create a registration abstraction when there are no feature routers. A
route-registration boundary becomes active with the first real feature:

```text
feature APIRouter
    ↓
application route registration
    ↓
FastAPI app
```

Registration may stay directly in `main.py`. Extract a separate module only when
registration composition has a real distinct responsibility or the target project
already requires that convention. A future need to register routers does not justify
a placeholder `registration.py` during an empty Bootstrap.

### Do not invent endpoints

Bootstrap must not invent product or operational endpoints to make the application
look complete. Do not automatically add:

- `/health`, `/healthz`, `/ready`, `/readiness`, `/live`, `/liveness`, `/ping`, or
  `/status`;
- demo or example endpoints;
- a fake feature merely to exercise routing;
- a placeholder router merely to have something to register.

Create such endpoints only when the user explicitly requests them, they are an
established standard in the target project, or a concrete deployment or infrastructure
requirement needs them now. Bootstrapping a FastAPI application is not by itself a
reason to add a health endpoint.

An application with no business routes is a valid Bootstrap result. Verify it by
checking the complete baseline package tree, importing the application object,
confirming `FastAPI(...)` construction, and running the import or startup checks
available in the existing environment. Check router registration only when feature
routers actually exist. Do not create API surface or registration infrastructure
solely to test the architecture.

## Extend

Use to expand an existing project.

1. Decide whether the capability belongs to an existing feature or creates a new
   cohesive feature boundary.
2. Inspect the feature and its current `routes/base`, response, error, and query
   infrastructure before adding local helpers.
3. Reuse compatible shared capabilities; keep feature-specific query and business
   behavior in the feature base.
4. Preserve compatible public envelopes, metadata semantics, and project conventions.
5. Apply the invariants from `core.md` to new code.
6. Do not refactor unrelated legacy code.
7. If the existing architecture differs but works, do not replace it silently.

## Audit

Audit is read-only. Review:

- feature boundaries;
- CBV inheritance;
- router thickness;
- separation of `model_mixins/` from `routes/base/mixins/`;
- shared success and error response normalization;
- collection count, pagination, empty-page, search, filter, and ordering behavior;
- alignment between projections, response envelopes, and Pydantic contracts;
- ORM/response separation;
- eager loading;
- transaction ownership;
- authentication and authorization boundaries;
- integration boundaries;
- explicit exports;
- Python class method order.

Classify findings with the categories in `core.md`. For each problem, provide concrete
evidence, its impact, and the smallest reasonable correction. Separate correctness
risks from consistency-only differences.
