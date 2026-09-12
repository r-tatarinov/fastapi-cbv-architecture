# Operating Modes

Select one mode and apply the invariants from [core.md](core.md). When the work touches
shared responses, errors, query parameters, or list behavior, also apply
[routing-infrastructure.md](routing-infrastructure.md).

## Bootstrap

Use for a new or minimal project.

1. Read [bootstrap.md](bootstrap.md) in full, together with the shared routing rules.
2. Inspect the target layout and preserve explicit user choices or existing setup.
3. Implement the starter's application setup, configuration, ORM/session boundary,
   task lifecycle, shared routing contracts, JSON responses/downloads, and docs auth.
4. Implement and register the `records` example with its model, entity mixin,
   feature base, thin CBV router, schemas, and migration.
5. Supply environment examples, dependencies, Docker/PostgreSQL startup, migrations,
   and concise commands for running the project and adding its next feature.
6. Run the acceptance checks in `bootstrap.md`; report any environment-limited checks.

### What counts as complete

The shared implementations are part of the starter contract, not optional future
work. A tree of `__init__.py` files or an importable FastAPI object alone is incomplete.
The generated project must let the developer start the application and add a feature
using the existing response, query, ORM, and setup abstractions.

The standard API surface consists of the small example and protected documentation.
Do not add other demo domains, health endpoints, identity providers, or integrations
unless requested or required by the target deployment. The `records` example may be
replaced by a user-requested first feature that demonstrates the same boundaries.
An explicit request to omit examples overrides the default but does not remove the
working shared infrastructure.

Keep the skill instruction-based. Do not require access to external reference
projects, templates, or repositories in order to apply this skill. Do not introduce
a bundled project template or generator merely to implement these instructions.

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

The Bootstrap inventory is not a retrofit checklist. Do not add its example,
documentation authentication, Docker setup, or other unrelated infrastructure to an
existing project as part of Extend.

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
