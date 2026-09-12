---
name: fastapi-cbv-architecture
description: Bootstrap, extend, or audit a feature-oriented Python/FastAPI application that follows the established CBV, ORM-manager, route-base, and entity-response patterns. Use for new project structure, API features, or architecture review; do not use to redesign working project infrastructure.
metadata:
  short-description: Apply the established FastAPI CBV architecture
---

# FastAPI CBV Architecture

Use this skill to bootstrap, extend, or audit a feature-oriented FastAPI application
whose routers use `fastapi-utils` CBVs and feature-local base classes.

The architecture is source-fidelity oriented. Reuse the established file placement,
inheritance, public method signatures, and class/function ownership. Removing an
irrelevant domain capability is allowed; silently replacing a known implementation
with a newly designed alternative is not.

## Select a mode

- **Bootstrap** — create the fixed minimal project from `assets/bootstrap/` by using
  `scripts/bootstrap_project.py`.
- **Extend** — add a requested capability while preserving the target project's
  established implementation patterns.
- **Audit** — perform a read-only assessment and report deviations.

Infer the mode from the requested outcome. Review requests use Audit and do not
authorize edits.

## Required references

- Read [references/core.md](references/core.md) for the normative architecture.
- Read [references/modes.md](references/modes.md) for the selected workflow.
- In Bootstrap, read [references/bootstrap.md](references/bootstrap.md) in full.
- When work touches shared responses, query parameters, filtering, pagination, or
  route-base classes, read
  [references/routing-infrastructure.md](references/routing-infrastructure.md).

## Non-negotiable boundaries

- Never create a host `.venv`, run a host dependency installer, or select a package
  manager on the user's behalf. Use an existing project/container workflow when the
  user requests runtime validation; otherwise run static checks.
- Do not synthesize Bootstrap Python files. Copy the bundled assets through the
  scaffold script so known modules keep their exact symbol ownership.
- Do not add examples, demo endpoints, migrations, tests, documentation auth, task
  runners, health routes, repositories, services, or integrations unless requested.
- In an existing project, do not apply the Bootstrap template over working files.

## Out of scope

This skill does not define billing, translations beyond the bundled response metadata
support, events/hooks, media, entitlements, or external-service architectures. Use the
target project's own contracts for those subsystems.
