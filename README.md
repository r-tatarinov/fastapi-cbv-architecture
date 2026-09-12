# FastAPI CBV Architecture

FastAPI CBV Architecture is a reusable architecture skill for AI coding agents and
developers working with feature-oriented FastAPI applications. It documents an
architecture convention built around FastAPI `APIRouter` feature routers registered
with `fastapi-utils` `@cbv(...)`, feature-local behavior bases, shared routing and
response infrastructure, thin HTTP boundaries, explicit ORM/entity-representation
separation, representation-driven eager loading, single-owner transactions, and
layers created only on demand.

It is not a FastAPI framework, Python library, or mandatory way to build FastAPI
applications.

## Why

FastAPI features can gradually mix HTTP wiring, database access, serialization,
response envelopes, collection querying, transactions, and integrations in the same
module. This skill provides a compact set of boundaries for keeping those
responsibilities visible without automatically adding service, repository, or other
speculative layers.

## Architecture

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

This is a responsibility flow; an endpoint uses only the layers its use case needs.

See [`references/core.md`](references/core.md) for the full normative architecture and
[`references/routing-infrastructure.md`](references/routing-infrastructure.md) for the
shared response, error, and collection-query boundaries.

## Feature structure

```text
routes/<feature>/
├── __init__.py
├── router.py
├── base.py
├── models.py
└── response_models.py  # optional OpenAPI responses/examples
```

Feature `models.py` contains Pydantic request, query, and response contracts.
`response_models.py`, when present, contains only OpenAPI `responses` metadata and
examples. Shared HTTP/API behavior lives separately from entity behavior:

```text
routes/base/
├── ...
└── mixins/
    └── ...             # response, error, and routing behavior

models/
├── __init__.py
└── <entity>.py

model_mixins/
├── __init__.py
└── <entity>/
    └── ...
```

## Core principles

- A feature is a cohesive API capability, and additional layers exist only when they
  have a current distinct responsibility.
- `fastapi-utils` `@cbv(...)` registers each feature router over a FastAPI `APIRouter`;
  the router class inherits its feature-local base.
- Routers own HTTP wiring and delegation, not SQL or business behavior.
- `routes/base/` owns shared routing infrastructure; `routes/base/mixins/` owns small,
  reusable HTTP/API behaviors such as response normalization and collection flow.
- ORM persistence and API representation are separated; one entity's representation
  is centralized under `model_mixins/` when the entity is API-facing.
- Model mixins never own HTTP behavior, and route-base mixins never become serializers
  for a particular entity.
- Composite and use-case-specific results, searches, filters, and ordering are owned by
  the feature base.
- Shared success and expected-error responses use one public envelope; feature-local
  Pydantic models declare that contract.
- Eager loaders are derived from the selected representation or projection.
- Serializer-triggered lazy SQL is forbidden.
- One atomic mutation has one transaction owner and one session across its database
  flow.

## Operating modes

```text
Bootstrap -> establish the architecture
Extend    -> add a capability to an existing application
Audit     -> review an existing architecture without modifying it
```

See [`references/modes.md`](references/modes.md) for Bootstrap, Extend, and Audit
workflows.

## Installation

Clone the repository:

```bash
git clone https://github.com/r-tatarinov/fastapi-cbv-architecture.git
```

To install it directly as a project-local skill under `.agents/skills`:

```bash
git clone https://github.com/r-tatarinov/fastapi-cbv-architecture.git \
  .agents/skills/fastapi-cbv-architecture
```

Other coding agents may use a different skills directory or discovery convention. You
can also copy the repository into that directory. The skill entrypoint is
[`SKILL.md`](SKILL.md).

## Repository structure

```text
fastapi-cbv-architecture/
├── SKILL.md
├── README.md
├── LICENSE
├── .gitignore
└── references/
    ├── core.md
    ├── routing-infrastructure.md
    └── modes.md
```

## Scope

This repository defines a feature-oriented FastAPI CBV architecture convention and
the Bootstrap, Extend, and Audit workflows for applying it.

It does not define billing, translations, events/hooks, media, entitlement systems,
specific external integration architectures, generic DDD, or a mandatory
service/repository architecture.

## License

Licensed under the [MIT License](LICENSE).
