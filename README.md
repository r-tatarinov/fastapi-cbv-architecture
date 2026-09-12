# FastAPI CBV Architecture

`fastapi-cbv-architecture` is a reusable skill for bootstrapping, extending, and
auditing a feature-oriented FastAPI application built with `fastapi-utils` CBVs.

The Bootstrap is a fixed, reduced source template. It preserves the established
locations and APIs of the application entrypoint, `ManagerSQLAlchemy`, route bases,
shared response mixin, ORM models, and flat entity-response mixins. It deliberately
does not redesign those components for a new project.

## Bootstrap

```bash
python scripts/bootstrap_project.py /path/to/project \
  --project-name "My API" \
  --port 2309
```

The generated project contains the core Python source plus Docker configuration. It
does not contain a demo feature, migrations, tests, task runners, protected docs, or a
host virtual environment. The script never installs dependencies or runs Docker.

See [references/bootstrap.md](references/bootstrap.md) for the exact inventory and
[references/core.md](references/core.md) for the architecture.

## Modes

- **Bootstrap** copies the bundled template into a new project.
- **Extend** follows the target project's active conventions and adds only requested
  capabilities.
- **Audit** reports architectural deviations without editing.

Shared response and collection behavior is documented in
[references/routing-infrastructure.md](references/routing-infrastructure.md).

## Validation

```bash
python scripts/validate_bootstrap.py
```

The validator checks the asset inventory, Python syntax, generated symbol ownership,
domain-neutral shared routing contracts, conflict handling, project substitutions,
and absence of `.venv` creation.

## License

Licensed under the [MIT License](LICENSE).
