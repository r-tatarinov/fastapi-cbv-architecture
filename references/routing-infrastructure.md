# Shared Routing Infrastructure

Read this document when work touches `routes/base`, route-base mixins, response
envelopes, error responses, common query parameters, or collection endpoints. Apply
the ownership rules from [core.md](core.md) first.

## Responsibility map

```text
routes/base/
    shared routing contracts and orchestration

routes/base/mixins/
    small reusable HTTP/API behaviors

routes/<feature>/base.py
    feature query, mutation, authorization that needs feature state,
    business validation, projection selection, transaction completion

routes/<feature>/router.py
    decorators, HTTP parameters, dependency/session wiring, response metadata,
    delegation

routes/<feature>/models.py
    Pydantic request, query, and response contracts
```

Shared routing code is an infrastructure boundary, not a generic home for code used
by more than one class. Promote behavior into it only when the behavior has the same
HTTP/API semantics across features and a stable extension point.

Prefer capability composition over a catch-all base:

```text
response envelope capability ─┐
error response capability ────┼─> FeatureBase -> FeatureRouter
collection query capability ──┘
```

A feature should inherit or delegate to only the capabilities it uses. Exact class and
method names follow the target project; names such as `ResponseMixin` or
`CollectionQueryMixin` describe responsibilities, not a required API.

## Successful responses

Use one shared response boundary to turn feature results into the project's public
HTTP envelope. In the architecture this commonly means:

```text
feature result
    + status code
    + optional metadata
    + optional established delivery options
                ↓
shared response builder
                ↓
{data: ..., success: true, meta?: ...}
```

The response capability owns:

- the stable envelope and the success flag;
- derivation of success/failure from the HTTP status class so callers cannot emit a
  status and a contradictory flag;
- propagation of the intended HTTP status;
- inclusion and normalization of shared metadata;
- headers and serialization format when the project has an established cross-feature
  delivery contract;
- the empty-list response shape for collection endpoints.

The response capability does not own ORM queries, feature business rules, entity
serialization, or the choice between an entity projection and a composite projection.
Keep one normalization path instead of constructing slightly different envelopes in
routers and feature bases.

JSON is the baseline. XML, YAML, downloads, or similar formats are optional transport
capabilities: preserve them when they are part of the target API, but do not add them
to a project merely because an earlier implementation supported them.

## Error responses

Expected feature failures use the same response boundary as successful results:

```text
feature/base detects expected failure
                ↓
error payload + semantic HTTP status
                ↓
shared response builder
                ↓
{data: {error: ...}, success: false}
```

- The feature base decides that a resource is absent, a conflict exists, or a business
  rule failed. It supplies the feature-specific message, safe details, and status.
- Route-base mixins may provide helpers for genuinely shared errors such as the
  application's standard authentication, permission, not-found, or conflict shape.
- A helper must delegate to the same response builder; it must not introduce a second
  envelope or hide the status code.
- Do not put feature names, domain lookups, or feature-specific validation in a common
  error mixin.
- Framework request-validation errors, raised `HTTPException`s, and unexpected
  exceptions remain the responsibility of FastAPI or registered exception handlers.
  Do not convert every exception into a route-mixin return value.
- Never expose database, credential, or remote-service internals merely because the
  envelope supports a `detail` field.

When an error is part of a public endpoint contract, declare its Pydantic schema in the
feature's `models.py` and reference it from the endpoint's OpenAPI `responses` metadata.

## Collection query flow

Use the shared collection flow only for endpoints whose semantics actually match it.
The feature base still owns the root statement and all domain-specific criteria.

```text
feature root statement + visibility/eligibility criteria
                         ↓
feature search/filter/order hooks
                         ↓
count matching rows before pagination
                         ↓
apply offset/start and limit
                         ↓
execute and select entity or composite projection
                         ↓
shared list metadata + response envelope
```

The common layer may own:

- stable query concepts such as offset/start, limit, ordering, search, and filtering;
- offset/limit application;
- total-count execution over the filtered, unpaginated statement;
- parsing a project-wide filter syntax and applying safe generic scalar filters;
- construction of list metadata and the empty-page response.

The feature base owns:

- the selected ORM entities, joins, eager loaders, and visibility criteria;
- the allowed filter keys and any relation-aware or domain-specific filters;
- explicit search expressions over real feature fields;
- the allowed ordering map and deterministic default order;
- the selected `data`, `data_by_list`, other entity projection, or composite builder.

Preserve established metadata field names when extending an existing API. Conceptually
distinguish the number of items returned on the current page from the total number of
matching items. Count from the filtered statement before offset/limit unless the
endpoint contract explicitly defines another meaning. The count must describe the same
logical entity population as the item query; use distinct counting when joins could
duplicate root entities.

Do not copy these historical implementation details into new infrastructure:

- a placeholder search against a guessed column such as `field` or `menutitle`;
- accepting arbitrary client-provided ORM attribute names without an allowlist;
- silently treating invalid filter values as valid filters;
- re-querying a page by collected IDs when the selected query can safely load and
  project the required rows directly;
- abstract methods that force unrelated features to implement empty stubs.

## Query contracts

Common dependency or Pydantic contracts may expose the subset shared by the project,
for example `start`/`offset`, `limit`, `order_by`, `search`, and `filter_by`. A
feature-local contract specializes validation, supported ordering values, descriptions,
and feature-only parameters.

- Bound offsets and limits according to the target API's compatibility requirements.
- Normalize optional values once at the contract boundary.
- Keep filter syntax stable when an existing public API uses it.
- For a new API, reject malformed filters, unknown keys, and invalid typed values with
  the project's normalized client-error response. Preserve a documented ignore policy
  only when compatibility with an existing API requires it.
- Treat response format and download flags as common parameters only when the shared
  response infrastructure implements them.

## Entity projections and API contracts

The layers cooperate without sharing ownership:

```text
ORM model
    -> persistence state

model_mixins/<entity>/
    -> one entity's `data*` representations

routes/<feature>/base.py
    -> chooses a representation or builds a composite result

routes/base/mixins/
    -> wraps the result as a public HTTP response

routes/<feature>/models.py
    -> declares the public Pydantic shape
```

The selected representation, eager-load graph, response envelope, and Pydantic schema
must describe the same payload. Update them together when a field or relation changes.

Returning a ready-made Starlette/FastAPI `Response` can bypass normal
`response_model` validation and serialization. If the shared builder returns a
`Response`, treat Pydantic models as an explicit public contract and verify the emitted
success, error, empty-list, and metadata payloads with endpoint tests. If the project
returns plain Python values and lets FastAPI serialize them, preserve that established
boundary instead of adding a custom `Response` wrapper.

## Placement and migration

For a new project, create `routes/base/` and `routes/base/mixins/` as Bootstrap package
boundaries. Place shared routing capabilities under `routes/base/` and reusable
HTTP/API mixins under `routes/base/mixins/` only when a concrete application-wide
contract requires them. The boundary packages may contain only `__init__.py` before
then; do not add placeholder response builders, error helpers, base classes, or
registries. In an existing project, classify older locations such as a top-level
`routes/mixins.py` or `routes/utils.py` before moving them. Their behavior may confirm
the architecture without their physical placement being precedent for new code.

Do not move working legacy infrastructure merely to make the tree look canonical.
When a requested change includes consolidation, move one coherent capability at a
time, preserve its public envelope, and update all consumers in the same change.
