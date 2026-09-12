#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ASSET_FILES = (
    ".dockerignore",
    ".gitignore",
    "Dockerfile",
    "docker-compose.yml",
    "src/.env.example",
    "src/__init__.py",
    "src/requirements.txt",
    "src/run.py",
    "src/app/__init__.py",
    "src/app/config.py",
    "src/app/i18n/__init__.py",
    "src/app/i18n/context.py",
    "src/app/models/__init__.py",
    "src/app/models/base.py",
    "src/app/models_mixins_data_responses/__init__.py",
    "src/app/orm_sender/__init__.py",
    "src/app/orm_sender/manager_sqlalchemy.py",
    "src/app/orm_sender/utils.py",
    "src/app/routes/__init__.py",
    "src/app/routes/general_models.py",
    "src/app/routes/mixins.py",
    "src/app/routes/utils.py",
    "src/app/routes/base/__init__.py",
    "src/app/routes/base/abstract_routes.py",
    "src/app/routes/base/general_routes.py",
)

TEXT_SUBSTITUTIONS = {
    "__PROJECT_NAME_LITERAL__": lambda project_name, _port: repr(project_name),
    "__PROJECT_PORT__": lambda _project_name, port: str(port),
}


def asset_root() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "bootstrap"


def validate_assets(root: Path) -> None:
    actual = tuple(
        sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())
    )
    expected = tuple(sorted(ASSET_FILES))
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        unexpected = sorted(set(actual) - set(expected))
        raise RuntimeError(f"Invalid Bootstrap assets: missing={missing}, unexpected={unexpected}")


def render_asset(source: Path, project_name: str, port: int) -> str:
    content = source.read_text(encoding="utf-8")
    for token, replacement in TEXT_SUBSTITUTIONS.items():
        content = content.replace(token, replacement(project_name, port))
    if "__PROJECT_" in content:
        raise RuntimeError(f"Unresolved project token in {source}")
    return content


def scaffold(target: Path, project_name: str | None = None, port: int = 2309) -> list[Path]:
    root = asset_root()
    validate_assets(root)

    resolved_name = project_name or target.resolve().name
    if not resolved_name.strip():
        raise ValueError("Project name must not be empty")

    conflicts = [target / relative for relative in ASSET_FILES if (target / relative).exists()]
    if conflicts:
        formatted = ", ".join(str(path) for path in conflicts)
        raise FileExistsError(f"Bootstrap would overwrite existing files: {formatted}")

    rendered = {
        relative: render_asset(root / relative, resolved_name, port)
        for relative in ASSET_FILES
    }
    written: list[Path] = []
    for relative in ASSET_FILES:
        source = root / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered[relative], encoding="utf-8")
        shutil.copymode(source, destination)
        written.append(destination)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the fixed FastAPI CBV Bootstrap")
    parser.add_argument("target", type=Path)
    parser.add_argument("--project-name")
    parser.add_argument("--port", type=int, default=2309)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    return args


def main() -> None:
    args = parse_args()
    written = scaffold(args.target, project_name=args.project_name, port=args.port)
    print(f"Created {len(written)} files in {args.target}")


if __name__ == "__main__":
    main()
