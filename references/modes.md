# Operating Modes

Select one mode and apply the invariants from [core.md](core.md).

## Bootstrap

Use for a new or minimal project.

1. Determine the package layout, application entrypoint, and existing infrastructure.
2. Create the minimum runnable architecture.
3. If there is a real first feature, apply the feature structure from `core.md`.
4. Add persistence or integrations only when the use case requires them.
5. Do not create placeholder layers.

## Extend

Use to expand an existing project.

1. Decide whether the capability belongs to an existing feature or creates a new
   cohesive feature boundary.
2. Inspect the relevant current architecture.
3. Preserve compatible project conventions.
4. Apply the invariants from `core.md` to new code.
5. Do not refactor unrelated legacy code.
6. If the existing architecture differs but works, do not replace it silently.

## Audit

Audit is read-only. Review:

- feature boundaries;
- CBV inheritance;
- router thickness;
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
