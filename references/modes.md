# Operating Modes

Select one mode and apply [core.md](core.md). Read
[routing-infrastructure.md](routing-infrastructure.md) when shared routing behavior is
in scope.

## Bootstrap

Use Bootstrap only for a new or intentionally empty project.

1. Inspect the target and confirm that scaffold paths do not already exist.
2. Read [bootstrap.md](bootstrap.md).
3. Run `scripts/bootstrap_project.py`; do not recreate its files manually.
4. Do not install host dependencies or create an environment.
5. Run static validation. Use the generated Docker workflow for runtime checks only
   when requested and available.

Bootstrap is complete when the fixed inventory is present and validates. It does not
need an endpoint, mapped entity, migration, database container, or test suite.

## Extend

Use Extend for an existing application or for the first real feature after Bootstrap.

1. Inspect the target's files and project instructions before choosing a pattern.
2. Preserve established paths, imports, public signatures, response shapes, session
   creation, and inheritance order when they are compatible with the request.
3. Put endpoint decorators and HTTP/session wiring in the feature router and reusable
   feature behavior in its base.
4. Add an ORM model and response mixin only for a real entity. Use one mapped model
   per file and one flat response-mixin module per API-facing model.
5. Add shared behavior only when it has a current cross-feature responsibility.
6. Do not refactor unrelated legacy code or replace existing infrastructure silently.

The Bootstrap inventory is never a retrofit checklist.

## Audit

Audit is read-only. Check:

- feature-local CBV inheritance and router/base ownership;
- physical placement of ORM models and flat entity-response mixins;
- `ManagerSQLAlchemy` fidelity and session use;
- shared response and collection-query contracts;
- eager-loading completeness and serializer-triggered SQL;
- transaction ownership;
- class method grouping: instance methods, then class methods, then static methods;
- extra modules or abstractions that are not present in the active project pattern.

For each finding, give evidence, impact, and the smallest correction. Distinguish a
working legacy exception from a newly introduced divergence.
