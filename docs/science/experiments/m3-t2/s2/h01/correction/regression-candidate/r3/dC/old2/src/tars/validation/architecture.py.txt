"""Static architecture checks (proof/architecture.md), enforced by code.

- The core must run without any LLM/model-provider SDK.
- No 3D/rendering dependency may enter the headless core (architecture rule 6).
- The physics core (tars.sim, tars.astro) must not use hidden non-determinism
  (randomness, wall-clock time, OS entropy, dynamic imports) or import validation code.

Checks cover absolute and relative imports and attribute access through import
aliases (e.g. ``np.random.default_rng``), per external review REV-005. This is a
static guard; byte-identical replay (determinism validator) is the dynamic one.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

FORBIDDEN_EVERYWHERE = {
    # LLM / model-provider SDKs and agent frameworks
    "anthropic", "openai", "google.generativeai", "google.genai", "langchain",
    "langchain_core", "langchain_openai", "llama_index", "cohere", "mistralai",
    "ollama", "litellm", "transformers",
    # 3D / rendering / game engines
    "godot", "pygame", "panda3d", "ursina", "pyglet", "OpenGL", "vtk", "moderngl",
    "arcade", "pyvista",
}  # fmt: skip
FORBIDDEN_IN_PHYSICS_CORE = {
    "random", "numpy.random", "secrets", "uuid", "time", "datetime", "os",
    "importlib", "tars.validation",
}  # fmt: skip
PHYSICS_CORE_PACKAGES = ("sim", "astro")


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    module: str
    rule: str


def _absolute(module: str | None, level: int, package: tuple[str, ...]) -> str:
    """Resolve ``from <level dots><module> import ...`` relative to ``package``."""
    if level == 0:
        return module or ""
    base = package[: len(package) - (level - 1)]
    return ".".join([*base, *([module] if module else [])])


def _dotted(node: ast.AST) -> list[str] | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return [node.id, *reversed(parts)]
    return None


def _referenced_modules(tree: ast.AST, package: tuple[str, ...]) -> Iterable[tuple[int, str]]:
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[(alias.asname or alias.name).split(".")[0]] = (
                    alias.name if alias.asname else alias.name.split(".")[0]
                )
                yield node.lineno, alias.name
        elif isinstance(node, ast.ImportFrom):
            module = _absolute(node.module, node.level, package)
            yield node.lineno, module
            for alias in node.names:
                full = f"{module}.{alias.name}"
                aliases[alias.asname or alias.name] = full
                yield node.lineno, full
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            chain = _dotted(node)
            if chain and chain[0] in aliases:
                yield node.lineno, ".".join([aliases[chain[0]], *chain[1:]])


def _matches(module: str, forbidden: set[str]) -> bool:
    return any(module == f or module.startswith(f + ".") for f in forbidden)


def scan(src_root: Path) -> list[Violation]:
    """Scan ``src_root`` (the ``src/tars`` package directory) for violations."""
    violations: set[Violation] = set()
    for path in sorted(src_root.rglob("*.py")):
        rel = path.relative_to(src_root)
        package = (src_root.name, *rel.parts[:-1])
        in_core = rel.parts[0] in PHYSICS_CORE_PACKAGES
        tree = ast.parse(path.read_text(), filename=str(path))
        for line, module in _referenced_modules(tree, package):
            if _matches(module, FORBIDDEN_EVERYWHERE):
                violations.add(Violation(str(rel), line, module, "llm_or_3d_dependency"))
            elif in_core and _matches(module, FORBIDDEN_IN_PHYSICS_CORE):
                violations.add(Violation(str(rel), line, module, "physics_core_nondeterminism"))
    return sorted(violations, key=lambda v: (v.path, v.line, v.module))
