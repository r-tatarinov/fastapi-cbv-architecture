# Core Architecture

This document is the normative architecture for this skill.

## Architecture map

A typical project may have this shape:

```text
app/
├── main.py
├── routes/
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   ├── ...                 # shared routing infrastructure
│   │   └── mixins/
│   │       └── ...             # reusable HTTP/API behavior
│   └── <feature>/
│       ├── __init__.py
│       ├── router.py
│       ├── base.py
│       ├── models.py
│       └── response_models.py  # optional OpenAPI responses/examples
│
├── database/
│   └── session.py
│
├── integrations/
│   └── <system>/
│       └── client.py
│
├── models/
│   ├── __init__.py
│   └── <entity>.py
│
└── model_mixins/
    ├── __init__.py
    └── <entity>/
        └── ...
```

> Create only the layers that have a current responsibility.

This tree shows architectural form, not mandatory literal paths. Adapt top-level
package names and placement to the existing project. Do not create empty or speculative
layers to resemble the example.

The runtime responsibility flow is:

```text
HTTP request
    ↓
routes/<feature>/router.py
    ↓
routes/<feature>/base.py
    ↓
ORM / integration
    ↓
entity representation or feature projection
    ↓
routes/base response infrastructure
    ↓
HTTP response
```

This is a responsibility model, not a requirement that every endpoint traverse every
possible layer. A use case stops where its current responsibilities stop.

`routes/<feature>/models.py` contains the feature's Pydantic request, parameter, and
response contracts. An optional `routes/<feature>/response_models.py` contains only
OpenAPI `responses` metadata and examples. `models/<entity>.py` contains ORM
persistence mapping; `model_mixins/<entity>/` contains that entity's response/data
behavior; and `routes/base/mixins/` contains reusable HTTP/API behavior.

| Question | Owner |
|---|---|
| Where is HTTP wiring? | Feature `router.py` |
| Where is feature behavior? | Feature `base.py` |
| Where is shared routing infrastructure? | `routes/base/` |
| Where are shared response and routing behaviors? | `routes/base/mixins/` |
| Where is persistence mapping? | `models/<entity>.py`, one mapped model per file |
| Where is one entity represented? | Its data/representation mixin under `model_mixins/<entity>/` |
| Where is a composite response built? | Feature `base.py` |
| Where are public API contracts? | Feature Pydantic `models.py` |
| Where are optional OpenAPI response examples? | Feature `response_models.py` |
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
├── models.py
└── response_models.py  # optional
```

- `router.py` owns the HTTP boundary: decorators, parameters, dependency injection,
  authentication wiring, session injection, response metadata, and delegation.
- `base.py` owns queries, mutations, business validation, result construction, and
  reusable feature behavior.
- `models.py` owns Pydantic request, parameter, and response contracts.
- `response_models.py`, when present, owns only OpenAPI `responses` metadata and
  examples; it does not own Pydantic API schemas.
- `__init__.py` owns explicit public exports used to register or consume the feature.

## Shared routing boundary

`routes/base/` is the shared infrastructure layer between feature behavior and the
HTTP response. It may define response-envelope construction, common error
normalization, collection-query orchestration, common query contracts, and small
reusable routing mixins when they implement an established application-wide contract
or repeated cross-feature behavior.

`routes/<feature>/base.py` composes only the shared capabilities that the feature
actually needs. It remains responsible for feature queries, mutations, business
rules, explicit search and ordering expressions, visibility criteria, and choosing an
entity representation or composite projection. `routes/<feature>/router.py` inherits
that feature base and remains the HTTP boundary.

Read [routing-infrastructure.md](routing-infrastructure.md) for the response, error,
list, pagination, filter, search, and contract-alignment rules.

## Two mixin families

Keep these sibling responsibilities separate even when historical projects use
different physical names:

```text
model_mixins/
    -> behavior and representations belonging to one ORM entity
       (`data`, `data_by_list`, other entity-specific `data*` projections)

routes/base/mixins/
    -> reusable HTTP/API response and routing behavior
       (response envelopes, error normalization, collection/query flow)
```

A model mixin must not know about HTTP status codes, pagination, query parameters, or
download formats. A route-base mixin must not become the canonical serializer for a
particular ORM entity. Product-, billing-, or other domain-specific behavior does not
become shared routing infrastructure merely because several feature classes inherit
it.

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
    ↑
selected routes/base capabilities
```

The inheritance boundary remains:

```text
FeatureBase
    ↑
FeatureRouter
```

The feature base may inherit or delegate to narrowly scoped abstractions from
`routes/base/`. Do not require every feature to inherit one universal base or implement
irrelevant abstract hooks.

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
├── router                 required for the HTTP boundary
├── base                   required for HTTP feature behavior
├── Pydantic models        when API contracts exist
├── OpenAPI response file  only when separate examples/metadata improve clarity
├── shared route behavior  only when behavior is reused across features
├── ORM model              only when persistent mapped state exists
├── entity mixin           only for API-facing ORM entities
└── eager loaders          only when a response reads relations
```

Do not create an ORM model, repository, serializer, loader, or integration abstraction
only to complete a template.

## ORM and response boundary

Store one mapped ORM model per file. For an API-facing ORM entity, keep persistence
mapping and representation code in separate package trees:

```text
models/
├── __init__.py
└── product.py

model_mixins/
├── __init__.py
└── product/
    └── ...
```

```text
ProductDataMixin
        ↑
     Product
```

```text
ORM model         -> persistence mapping
Model/entity mixin -> behavior and representations of this ORM entity
Route-base mixin  -> reusable HTTP/API behavior
Pydantic model    -> public API contract
```

API serialization must not live directly in the mapped ORM model body. An internal or
link model that is not exposed through the API does not require an entity
data/representation mixin. Add that boundary only when the entity becomes API-facing.
Keep entity mixins in the dedicated `model_mixins/<entity>/` package, separate from
ORM mappings. Export
externally consumed models and mixins explicitly through their package `__init__.py`.

## Entity and response construction

Centralize representations of one ORM entity in its data/representation mixin:

- `data` may be its default representation;
- `data_by_list` may be a compact/list representation;
- other `data_*` or `data_by_*` builders are valid when they match project vocabulary.

Do not prescribe a global builder catalog.

```text
single ORM entity representation -> entity data/representation mixin

multiple entities /
computed fields /
aggregate projection             -> feature base

HTTP envelope /
status and metadata /
delivery representation          -> route-base response infrastructure
```

The feature base selects the entity builder or constructs the composite result, then
passes that result to the shared response infrastructure. The router must not assemble
ORM-derived payloads. JSON is the default delivery representation. Other formats or
download behavior belong in shared routing infrastructure only when they are an
established cross-feature API capability; do not create them speculatively.

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
