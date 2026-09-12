---
name: fastapi-cbv-architecture
description: Bootstrap, extend, or audit a feature-oriented Python/FastAPI application built around fastapi-utils CBV routers, thin HTTP wiring, explicit ORM response boundaries, eager relation loading, and single-owner transactions. Use when shaping the base application architecture, adding an API feature, or reviewing an existing FastAPI structure; do not use for subsystem-specific design.
metadata:
  short-description: Apply feature-oriented FastAPI CBV architecture
---

# FastAPI CBV Architecture

Use this skill to bootstrap, extend, or audit a feature-oriented FastAPI application
whose HTTP features use `fastapi-utils` CBV routers and feature-local behavior bases.

The architecture keeps HTTP wiring thin, places feature behavior behind the router,
separates persistence from API representation, derives eager loading from the selected
representation, and gives each atomic mutation one transaction owner. Create only the
layers that have a current responsibility, adapting package names and paths to the
existing project.

## Select a mode

- **Bootstrap** — establish a minimal runnable architecture in a new or minimal project.
- **Extend** — add a capability to an existing project without treating legacy patterns
  as automatic precedent.
- **Audit** — perform a read-only architecture assessment.

Infer the mode from the requested outcome when it is not named. Review or assessment
requests use Audit and do not authorize edits.

## References

- Read [references/core.md](references/core.md) for the normative architecture.
- Read [references/modes.md](references/modes.md) for the selected mode's workflow.

## Out of scope

This skill does not define subsystem architecture for billing, translations,
events/hooks, media, entitlement systems, or particular external services. It also
does not prescribe generic DDD, service, or repository architectures. Apply those
contracts from the target project's own context when they are relevant.
