---
name: fastapi-cbv-architecture
description: Bootstrap, extend, or audit a feature-oriented Python/FastAPI application built around fastapi-utils CBV routers, shared routing and response infrastructure, thin HTTP wiring, separate ORM entity representations, eager relation loading, and single-owner transactions. Use when shaping the base application architecture, adding an API feature, or reviewing an existing FastAPI structure; do not use for subsystem-specific design.
metadata:
  short-description: Apply feature-oriented FastAPI CBV architecture
---

# FastAPI CBV Architecture

Use this skill to bootstrap, extend, or audit a feature-oriented FastAPI application
whose HTTP features use `fastapi-utils` CBV routers and feature-local behavior bases.

The architecture keeps HTTP wiring thin, places feature behavior behind the router,
shares reusable HTTP response and collection-query behavior through the routing base,
separates persistence from entity representation, derives eager loading from the
selected representation, and gives each atomic mutation one transaction owner. During
Bootstrap, build the ready-to-develop application defined in `references/bootstrap.md`,
including working shared infrastructure and a small example feature. Outside that
baseline, create layers and modules with a current responsibility, adapting package
names and paths to the existing project.

## Select a mode

- **Bootstrap** — establish a runnable project with application setup, async ORM,
  shared routing abstractions, JSON responses/downloads, protected documentation,
  task lifecycle, migrations, Docker, and an example CBV feature.
- **Extend** — add a capability to an existing project without treating legacy patterns
  as automatic precedent.
- **Audit** — perform a read-only architecture assessment.

Infer the mode from the requested outcome when it is not named. Review or assessment
requests use Audit and do not authorize edits.

## References

- Read [references/core.md](references/core.md) for the normative architecture.
- Read [references/routing-infrastructure.md](references/routing-infrastructure.md)
  when the task touches shared response envelopes, errors, query parameters, list
  flows, pagination, filtering, searching, sorting, or `routes/base` abstractions.
- Read [references/modes.md](references/modes.md) for the selected mode's workflow.
- In Bootstrap, also read [references/bootstrap.md](references/bootstrap.md) in full
  for the required implementations and acceptance checks. These are instructions for
  generating a project, not a bundled code template or a dependency on a source repo.

## Out of scope

This skill does not define subsystem architecture for billing, translations,
events/hooks, media, entitlement systems, or particular external services. It also
does not prescribe generic DDD, service, or repository architectures. Apply those
contracts from the target project's own context when they are relevant.
