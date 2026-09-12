# Shared Routing Infrastructure

Read this document when work touches shared responses, query parameters, filtering,
pagination, or the route-base classes.

## Physical ownership

```text
routes/general_models.py
    shared HTTP parameter and response-schema classes

routes/utils.py
    response decorators and module utilities

routes/mixins.py
    MainRouterMIXIN and other established shared router mixins

routes/base/abstract_routes.py
    AbstractBaseRouter hooks

routes/base/general_routes.py
    GeneralBaseRouter collection flow

routes/<feature>/base.py
    feature queries, projections, validation, and mutations
```

Do not relocate these symbols merely to produce a cleaner-looking hierarchy.

## Shared response contract

`MainRouterMIXIN.get_data` keeps the established signature:

```python
get_data(data, status_code=200, meta=None, fmt="json", is_download=False)
```

It is a static method decorated by `make_data_by_response`. The decorator owns the
`{data, success, meta?}` envelope and JSON/YAML/XML download behavior. Preserve the
status code and the established metadata fields. Do not replace this contract with a
new response-builder function or split its methods among new modules during ordinary
feature work.

`GeneralParams` keeps `start`, `limit`, `order_by`, `response_fmt`, `is_download`,
`search`, `filter_by`, and `lang`. Extend may preserve a target project's narrower
variant, but Bootstrap must use the bundled contract without redesigning it.

## Collection flow

`GeneralBaseRouter` keeps these recognizable entry points and their existing calling
shape:

- `get_response_by_select_rel(session, params, select_rel, **kwargs)`;
- `get_instances_by_response(session, params, select_rel)`;
- `get_count_by_select_rel(session, select_rel, **kwargs)`;
- `apply_filter_by(filter_by, model_class, select_rel, allowed_keys=None)`;
- `parse_filter_by(filter_string, allowed_keys=None)`.

The shared base may inspect a requested filter field dynamically, but it must not name
or access a concrete model field directly. The feature base supplies its root
statement, ordering map, search expressions over known fields, specialized filtering,
loaders, and projection hooks. Shared code must not gain feature-specific models,
fields, or business rules. Preserve `meta.total` as the returned-page size and
`meta.counts` as the count produced by the established count flow.

`AbstractBaseRouter` declares only the hooks every collection feature is expected to
provide: collection orchestration, ordering, entity projection, and response
construction. Optional projections and relation-specific variants belong to the
feature that uses them rather than to the shared abstract base.

## Errors and extensions

Reuse the generic `MainRouterMIXIN` helpers when their public response matches the
feature. Field-, relation-, hierarchy-, and localization-specific errors belong in the
feature base. Do not add a parallel envelope system or generic exception catcher.

When changing a shared method, inspect every consumer and preserve its positional and
keyword calling conventions. A correctness fix that intentionally changes the public
contract requires explicit scope; it is not part of ordinary Bootstrap fidelity.
