# Core Architecture

This document is the normative architecture for this skill.

## Architecture map

A typical project may have this shape:

```text
app/
├── main.py
├── routes/
│   ├── __init__.py
│   └── <feature>/
│       ├── __init__.py
│       ├── router.py
│       ├── base.py
│       └── models.py
│
├── models/
│   ├── __init__.py
│   ├── <entity>.py
│   └── mixins/
│       ├── __init__.py
│       └── <entity>.py
│
├── database/
│   └── session.py
│
└── integrations/
    └── <system>/
        └── client.py
```

> Create only the layers that have a current responsibility.

This tree shows architectural form, not mandatory literal paths. Adapt top-level
package names and placement to the existing project. Do not create empty or speculative
layers to resemble the example.

The runtime responsibility flow is:

```text
HTTP request
    ↓
router.py
    ↓
base.py
    ↓
ORM / integration
    ↓
result construction / response builder
    ↓
Pydantic contract
    ↓
HTTP response
```

This is a responsibility model, not a requirement that every endpoint traverse every
possible layer. A use case stops where its current responsibilities stop.

`routes/<feature>/models.py` contains Pydantic API contracts;
`models/<entity>.py` contains ORM persistence mapping.

| Question | Owner |
|---|---|
| Where is HTTP wiring? | Feature `router.py` |
| Where is feature behavior? | Feature `base.py` |
| Where is persistence mapping? | `models/<entity>.py`, one mapped model per file |
| Where is one entity represented? | Its response/data mixin |
| Where is a composite response built? | Feature `base.py` |
| Where are public API contracts? | Feature Pydantic `models.py` |
| Who completes an HTTP transaction? | The feature-base mutation |
| What determines eager loaders? | Relations read by the selected builder or projection |
| When is a new layer created? | Only when it has a current distinct responsibility |

## Feature boundary

A feature is a cohesive API capability. It is not automatically one ORM table and is
not a broad domain bucket.

The baseline for a new HTTP feature is:

```text
routes/<feature>/
├── __init__.py
├── router.py
├── base.py
└── models.py
```

- `router.py` owns the HTTP boundary: decorators, parameters, dependency injection,
  authentication wiring, session injection, response metadata, and delegation.
- `base.py` owns queries, mutations, business validation, result construction, and
  reusable feature behavior.
- `models.py` owns Pydantic request, parameter, and response contracts.
- `__init__.py` owns explicit public exports used to register or consume the feature.

`response_models.py` is not part of the baseline. Add it only when the project uses
separate OpenAPI response metadata or examples that cannot reasonably remain in
`models.py`.

## CBV boundary

Each feature router uses a standard FastAPI `APIRouter` and is registered as a
class-based view with `fastapi_utils.cbv.cbv`. The `APIRouter` comes from FastAPI; the
CBV registration mechanism comes from `fastapi-utils`:

```text
APIRouter
    ↓
@cbv(router)
    ↓
FeatureRouter
    ↑
FeatureBase
```

The inheritance boundary remains:

```text
FeatureBase
    ↑
FeatureRouter
```

Structural example:

```python
from fastapi import APIRouter
from fastapi_utils.cbv import cbv


products_router = APIRouter()


class ProductsBase:
    async def get_product(self, ...):
        ...


@cbv(products_router)
class ProductsRouter(ProductsBase):
    @products_router.get(...)
    async def get(self, ...):
        return await self.get_product(...)
```

- Build every feature router around a regular FastAPI `APIRouter`.
- Decorate the router class with `@cbv(<feature_router>)` from `fastapi-utils`.
- Make the router class inherit its feature-local base.
- Keep route decorators on the feature `APIRouter`; endpoint handlers are instance
  methods and receive `self`.
- Call feature behavior through `self`, `cls`, or correct `super()` dispatch.
- Do not invoke a parent/base implementation directly by class name to bypass normal
  dispatch.
- Do not create a custom CBV registration mechanism or replace `fastapi-utils` with
  another CBV package unless the project's architecture standard explicitly changes.
- Name endpoint methods after the HTTP decorator verb: `get`, `post`, `put`, `patch`,
  or `delete`.

`fastapi-utils` is a dependency of the target FastAPI application that applies this
architecture, not a runtime dependency of this Markdown skill repository.

## Thin router invariant

```text
router.py may own:                 router.py must not own:
✓ HTTP parameters                 ✗ SQL
✓ decorators                      ✗ session.execute(...)
✓ dependency injection            ✗ ORM mutation
✓ authentication wiring           ✗ business validation
✓ session boundary                ✗ transaction completion
✓ response metadata               ✗ ORM-derived payload construction
✓ delegation
```

Do not create a service or repository layer automatically. Add another layer only when
it has a distinct current responsibility or an established project subsystem already
owns that responsibility.

## Layers on demand

```text
HTTP feature
├── router          required for the HTTP boundary
├── base            required for HTTP feature behavior
├── Pydantic models when API contracts exist
├── ORM model       only when persistent mapped state exists
├── response mixin  only for API-facing ORM entities
└── eager loaders   only when a response reads relations
```

Do not create an ORM model, repository, serializer, loader, or integration abstraction
only to complete a template.

## ORM and response boundary

Store one mapped ORM model per file. For an API-facing ORM entity, keep persistence and
representation in separate files:

```text
models/
├── product.py
└── mixins/
    └── product.py
```

```text
ProductResponseMixin
        ↑
     Product
```

```text
ORM model       -> persistence mapping
Response mixin  -> representation of this ORM entity
Pydantic model  -> public API contract
```

API serialization must not live directly in the mapped ORM model body. An internal or
link model that is not exposed through the API does not require a response mixin. Add
that boundary only when the entity becomes API-facing. Export externally consumed
models and mixins explicitly through their package `__init__.py`.

## Response construction

Centralize representations of one ORM entity in its response/data mixin:

- `data` may be its default representation;
- `data_by_list` may be a compact/list representation;
- other `data_*` or `data_by_*` builders are valid when they match project vocabulary.

Do not prescribe a global builder catalog.

```text
single ORM entity representation -> entity response mixin

multiple entities /
computed fields /
aggregate projection             -> feature base
```

The router must not assemble ORM-derived payloads. JSON is the default representation.
A file or download response is an endpoint-specific delivery variant, not a reason to
create a global response-format system.

## Relation loading

Derive the eager-load graph from the exact builder or projection that will run:

```text
response builder
      ↓
relations it reads
      ↓
eager-load graph
```

For example:

```text
Product.data
├── category
└── variants
    └── supplier
```

Every query path using `Product.data` must preload that complete relation graph.

- Include relations read by nested builders.
- Apply visibility or eligibility filtering in queries/loaders when it is part of the
  response contract.
- Prefer `selectinload(...)` for collections when it matches the query shape.
- Use `raiseload("*")` and `load_only(..., raiseload=True)` where compatible with the
  projection to expose undeclared access.
- If a builder starts reading a new relation, review and update every query path that
  uses that builder.

> Serializer-triggered lazy I/O is forbidden.

Serialization of a fully loaded object must not issue SQL.

## Transactions

One atomic mutation has one transaction owner and one session throughout its database
flow.

```text
router
  │
  │ session
  ▼
feature base mutation
  │
  ├── helper(session)
  ├── helper(session)
  ├── flush()
  └── commit()
```

For an HTTP mutation, the router creates or injects the session boundary and the
feature-base mutation owns transaction completion: it commits after the whole atomic
operation succeeds and rolls back on failure. Nested database methods:

```text
✓ accept the owner's session
✓ flush when intermediate database state is required

✗ create an independent session
✗ commit the owner's transaction
✗ roll back the owner's transaction
```

For non-HTTP flows, the transaction owner may be a task or explicit orchestrator.

> Database rollback cannot undo an external side effect.

Define ordering and, where partial failure matters, idempotency, retry, or compensation
at the integration/use-case boundary.

## Authentication and authorization

```text
authentication
    ↓
caller identity

authorization
    ↓
may this caller act on this resource?

business validation
    ↓
is the requested operation valid?
```

Authentication belongs to HTTP/DI wiring or an established authentication boundary.
Resource authorization that needs database state uses the same session as the mutation
flow. For a mutation, authenticate and authorize before business validation and state
change. Do not bind this architecture to a particular identity or permission provider.

## Integration boundaries

- `router.py` must not call external HTTP or storage systems directly.
- Reuse the project's client or adapter for the external system.
- If no boundary exists, create one focused abstraction only when the integration has
  a real transport or policy responsibility.
- Credentials, transport, protocol details, and remote error normalization belong to
  the integration boundary.
- Do not build a `service -> repository -> gateway -> adapter` chain without distinct
  current responsibilities.
- Do not copy remote-owned entities locally without explicit local ownership and a
  concrete reason.

## Existing projects

Classify observed implementations before using them as precedent:

- **conforms** — follows the active architecture;
- **legacy** — working historical deviation, not precedent for new code;
- **transitional** — intentional intermediate structure;
- **violation** — breaks an active invariant or creates a correctness risk;
- **allowed exception** — deliberate bounded alternative with a stated reason.

Normative project instructions outweigh incidental historical patterns. If the active
convention cannot be determined confidently, report the inconsistency rather than
silently selecting one variant. Do not mass-refactor legacy code merely to match the
current style.

## Python class order

For new or substantially changed classes, group methods in this order:

1. ordinary instance methods;
2. `@classmethod` methods;
3. `@staticmethod` methods.

Legacy classes with another order are not automatic cleanup scope.
