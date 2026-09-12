# Operating Modes

Select one mode and apply the invariants from [core.md](core.md). When the work touches
shared responses, errors, query parameters, or list behavior, also apply
[routing-infrastructure.md](routing-infrastructure.md).

## Bootstrap

Use for a new or minimal project.

1. Determine the package layout, application entrypoint, and existing infrastructure.
2. Create the minimum runnable architecture.
3. If there is a real first feature, apply the feature structure from `core.md`.
4. Add a shared response or collection-query capability only when a concrete feature
   uses it as an application-wide contract; do not scaffold an empty
   `routes/base/mixins/` catalog.
5. Add persistence or integrations only when the use case requires them.
6. Do not create placeholder layers, formats, or abstract hooks.

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

An application with no business routes is a valid bootstrap result. Verify it by
importing the application object, confirming `FastAPI(...)` construction, checking
router-registration infrastructure when it exists, and running the import or startup
checks available in the existing environment. Do not create API surface solely to test
the architecture.

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
