"""Enforces the hard rule (build guide sec. 3): a package under packages/* imports only from
``contracts`` and its own code - never another component's internals."""

import ast
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[1] / "packages"
COMPONENTS = {p.name for p in PACKAGES.iterdir() if p.is_dir() and (p / "__init__.py").exists()}


def imported_top_levels(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_no_cross_component_imports():
    violations = []
    for pkg in COMPONENTS - {"contracts"}:
        for py in (PACKAGES / pkg).rglob("*.py"):
            bad = (imported_top_levels(py) & COMPONENTS) - {"contracts", pkg}
            if bad:
                violations.append(f"{py.relative_to(PACKAGES)} imports {sorted(bad)}")
    assert not violations, "\n".join(violations)


def test_contracts_imports_nothing_internal():
    for py in (PACKAGES / "contracts").rglob("*.py"):
        assert not (imported_top_levels(py) & (COMPONENTS - {"contracts"}))
