# FastAPI CBV Architecture

FastAPI CBV Architecture is a reusable architecture skill for AI coding agents and
developers working with feature-oriented FastAPI applications. It documents an
architecture convention built around FastAPI `APIRouter` feature routers registered
with `fastapi-utils` `@cbv(...)`, feature-local behavior bases, thin HTTP boundaries,
explicit ORM/response separation, representation-driven eager loading, single-owner
transactions, and layers created only on demand.

It is not a FastAPI framework, Python library, or mandatory way to build FastAPI
applications.

## Why

FastAPI features can gradually mix HTTP wiring, database access, serialization,
transactions, and integrations in the same module. This skill provides a compact set
of boundaries for keeping those responsibilities visible without automatically adding
service, repository, or other speculative layers.

## Architecture

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

This is a responsibility flow; an endpoint uses only the layers its use case needs.

See [`references/core.md`](references/core.md) for the full normative architecture.

## Feature structure

```text
routes/<feature>/
├── __init__.py
├── router.py
├── base.py
├── models.py
└── response_models.py
```

Here, feature `models.py` contains Pydantic request and parameter contracts, while
`response_models.py` contains Pydantic response contracts. ORM mappings live
separately under the application's ORM models package. Entity response/data mixins
live in a sibling `model_mixins` package:

```text
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
- ORM persistence and API representation are separated; one entity's representation
  is centralized in its response/data mixin when the entity is API-facing.
- Composite and use-case-specific results are constructed in the feature base.
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
