#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import importlib.util
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = SKILL_ROOT / "assets" / "bootstrap"
PROJECT_NAME_TOKEN = "__PROJECT_NAME_LITERAL__"
PROJECT_PORT_TOKEN = "__PROJECT_PORT__"
FORBIDDEN_MANAGER_SYMBOLS = (
    "Base",
    "build_database_url",
    "get_session",
    "session_factory",
    "dispose",
)
PINNED_SOURCE_HASHES = {
    "src/app/orm_sender/manager_sqlalchemy.py": "e12a900ba37316e6fe630465afef107ebe7258a9da03828a57d1df28ce878e65",
    "src/app/orm_sender/utils.py": "2473c217a34940023cbfd199867db54aa9645af56106e686dd845e7d3e673f7a",
    "src/app/models/base.py": "f669d28157a174a75b75597885482e2aaebb04104b052494d08a6da0b8531355",
    "src/app/i18n/context.py": "0ac430eaba84e7465d0c7c15e693410b4a3458b9599cc9443ba3f7931348df62",
}


def load_scaffolder():
    path = SKILL_ROOT / "scripts" / "bootstrap_project.py"
    spec = importlib.util.spec_from_file_location("bootstrap_project", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load bootstrap_project.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def python_tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def class_method_names(path: Path, class_name: str) -> list[str]:
    classes = [
        node
        for node in python_tree(path).body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    ]
    assert len(classes) == 1, f"Expected one {class_name} in {path}"
    return [
        node.name
        for node in classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def validate_manager() -> None:
    path = ASSET_ROOT / "src/app/orm_sender/manager_sqlalchemy.py"
    tree = python_tree(path)
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    assignments = [node for node in tree.body if isinstance(node, (ast.Assign, ast.AnnAssign))]
    assert [node.name for node in classes] == ["ManagerSQLAlchemy"]
    assert not functions
    assert not assignments

    source = path.read_text(encoding="utf-8")
    for symbol in FORBIDDEN_MANAGER_SYMBOLS:
        assert symbol not in source, f"Unexpected manager symbol: {symbol}"
    engine_assignments = [
        node
        for node in classes[0].body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "engine" for target in node.targets)
    ]
    assert len(engine_assignments) == 1


def validate_pinned_source_files() -> None:
    for relative, expected_hash in PINNED_SOURCE_HASHES.items():
        actual_hash = hashlib.sha256((ASSET_ROOT / relative).read_bytes()).hexdigest()
        assert actual_hash == expected_hash, f"Pinned source file changed: {relative}"


def validate_python_files(root: Path) -> None:
    for path in root.rglob("*.py"):
        tree = python_tree(path)
        for class_node in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
            method_groups: list[int] = []
            for node in class_node.body:
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                decorators = {
                    decorator.id
                    for decorator in node.decorator_list
                    if isinstance(decorator, ast.Name)
                }
                if decorators & {"classmethod", "abstractclassmethod"}:
                    method_groups.append(1)
                elif decorators & {"staticmethod", "abstractstaticmethod"}:
                    method_groups.append(2)
                else:
                    method_groups.append(0)
            assert method_groups == sorted(method_groups), f"Invalid method order in {path}:{class_node.name}"


def validate_shared_routing_contract() -> None:
    expected_methods = {
        "src/app/routes/base/abstract_routes.py": (
            "AbstractBaseRouter",
            [
                "get_response_by_select_rel",
                "set_order_by",
                "get_data_by_response",
                "get_data",
            ],
        ),
        "src/app/routes/base/general_routes.py": (
            "GeneralBaseRouter",
            [
                "get_response_by_select_rel",
                "apply_filter_by",
                "get_instances_by_response",
                "make_response_by_data_of_zero",
                "apply_filter_by_model_field",
                "get_count_by_select_rel",
                "parse_filter_by",
            ],
        ),
        "src/app/routes/mixins.py": (
            "MainRouterMIXIN",
            [
                "make_response_by_ok",
                "make_response_by_error_not_exists",
                "make_response_by_error_already_exists",
                "make_response_by_format_file_error",
                "make_response_by_auth_error",
                "make_response_by_permission_error",
                "get_data",
            ],
        ),
    }
    for relative, (class_name, methods) in expected_methods.items():
        path = ASSET_ROOT / relative
        assert class_method_names(path, class_name) == methods, (
            f"Invalid shared routing contract: {relative}:{class_name}"
        )

    general_routes = python_tree(ASSET_ROOT / "src/app/routes/base/general_routes.py")
    concrete_model_fields = [
        node.attr
        for node in ast.walk(general_routes)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "model_class"
    ]
    assert not concrete_model_fields, (
        f"Shared routing accesses concrete model fields: {concrete_model_fields}"
    )


def validate_template_contract(scaffolder) -> None:
    assert set(scaffolder.TEXT_SUBSTITUTIONS) == {
        PROJECT_NAME_TOKEN,
        PROJECT_PORT_TOKEN,
    }

    token_locations: dict[str, list[str]] = {
        PROJECT_NAME_TOKEN: [],
        PROJECT_PORT_TOKEN: [],
    }
    for path in ASSET_ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ASSET_ROOT).as_posix()
        content = path.read_text(encoding="utf-8")
        for token in token_locations:
            token_locations[token].extend([relative] * content.count(token))
        assert content.count("__PROJECT_") == sum(
            content.count(token) for token in token_locations
        ), f"Unknown project substitution token in {relative}"

    assert token_locations == {
        PROJECT_NAME_TOKEN: ["src/app/__init__.py"],
        PROJECT_PORT_TOKEN: [
            "docker-compose.yml",
            "docker-compose.yml",
            "docker-compose.yml",
        ],
    }

    app_tree = python_tree(ASSET_ROOT / "src/app/__init__.py")
    title_values = [
        keyword.value
        for node in ast.walk(app_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "FastAPI"
        for keyword in node.keywords
        if keyword.arg == "title"
    ]
    assert len(title_values) == 1
    assert isinstance(title_values[0], ast.Name)
    assert title_values[0].id == PROJECT_NAME_TOKEN


def validate_generated_identity(root: Path, project_name: str) -> None:
    locations: list[str] = []
    for path in root.rglob("*"):
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            locations.extend([relative] * path.read_text(encoding="utf-8").count(project_name))
    assert locations == ["src/app/__init__.py"]

    app_tree = python_tree(root / "src/app/__init__.py")
    title_values = [
        keyword.value
        for node in ast.walk(app_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "FastAPI"
        for keyword in node.keywords
        if keyword.arg == "title"
    ]
    assert len(title_values) == 1
    assert isinstance(title_values[0], ast.Constant)
    assert title_values[0].value == project_name


def validate_compose_service(root: Path) -> None:
    content = (root / "docker-compose.yml").read_text(encoding="utf-8")
    service_names = [
        line.strip()[:-1]
        for line in content.splitlines()
        if line.startswith("    ")
        and not line.startswith("        ")
        and line.strip().endswith(":")
    ]
    assert service_names == ["api"]


def validate_no_host_environment_commands() -> None:
    checked = [SKILL_ROOT / "SKILL.md", *sorted((SKILL_ROOT / "references").glob("*.md"))]
    checked.extend(
        path
        for path in ASSET_ROOT.rglob("*")
        if path.is_file() and path.name not in {"Dockerfile", ".gitignore", ".dockerignore"}
    )
    forbidden = (" -m venv ", "virtualenv ", "uv sync", "poetry install", "pip install")
    for path in checked:
        content = f" {path.read_text(encoding='utf-8').lower()} "
        for command in forbidden:
            assert command not in content, f"Forbidden host environment command in {path}: {command}"


def validate_scaffold() -> None:
    scaffolder = load_scaffolder()
    scaffolder.validate_assets(ASSET_ROOT)
    validate_template_contract(scaffolder)

    with tempfile.TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
        target = root / "bootstrap-validation"
        project_name = "Bootstrap Validation Project"
        written = scaffolder.scaffold(target, project_name=project_name, port=2310)
        actual = tuple(sorted(path.relative_to(target).as_posix() for path in written))
        assert actual == tuple(sorted(scaffolder.ASSET_FILES))
        assert not (target / ".venv").exists()
        assert not (target / "src/app/main.py").exists()
        assert "2310:2310" in (target / "docker-compose.yml").read_text(encoding="utf-8")
        validate_python_files(target)
        validate_generated_identity(target, project_name)
        validate_compose_service(target)

        try:
            scaffolder.scaffold(target)
        except FileExistsError:
            pass
        else:
            raise AssertionError("A second scaffold must refuse existing files")

    with tempfile.TemporaryDirectory() as temporary_directory:
        target = Path(temporary_directory)
        conflict = target / "Dockerfile"
        conflict.write_text("user content\n", encoding="utf-8")
        try:
            scaffolder.scaffold(target)
        except FileExistsError:
            pass
        else:
            raise AssertionError("A conflicting scaffold must fail")
        assert conflict.read_text(encoding="utf-8") == "user content\n"
        assert sorted(path.name for path in target.iterdir()) == ["Dockerfile"]


def main() -> None:
    validate_manager()
    validate_pinned_source_files()
    validate_python_files(ASSET_ROOT)
    validate_shared_routing_contract()
    validate_no_host_environment_commands()
    validate_scaffold()
    print("Bootstrap assets are valid")


if __name__ == "__main__":
    main()
