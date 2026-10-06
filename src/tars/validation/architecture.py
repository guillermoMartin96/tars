"""Static architecture checks (proof/architecture.md), enforced by code.

- The core must run without any LLM/model-provider SDK.
- No 3D/rendering dependency may enter the headless core (architecture rule 6).
- The physics core (tars.sim, tars.astro) must not use hidden non-determinism
  (unseeded randomness, wall-clock time, UUIDs) or import validation code.
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
    "random", "numpy.random", "secrets", "uuid", "time", "tars.validation",
}  # fmt: skip
PHYSICS_CORE_PACKAGES = ("sim", "astro")


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    module: str
    rule: str


def _imported_modules(tree: ast.AST) -> Iterable[tuple[int, str]]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            yield node.lineno, node.module
            for alias in node.names:
                yield node.lineno, f"{node.module}.{alias.name}"


def _matches(module: str, forbidden: set[str]) -> bool:
    return any(module == f or module.startswith(f + ".") for f in forbidden)


def scan(src_root: Path) -> list[Violation]:
    """Scan ``src_root`` (the ``src/tars`` package directory) for violations."""
    violations: list[Violation] = []
    for path in sorted(src_root.rglob("*.py")):
        rel = path.relative_to(src_root)
        in_core = rel.parts[0] in PHYSICS_CORE_PACKAGES
        tree = ast.parse(path.read_text(), filename=str(path))
        for line, module in _imported_modules(tree):
            if _matches(module, FORBIDDEN_EVERYWHERE):
                violations.append(Violation(str(rel), line, module, "llm_or_3d_dependency"))
            elif in_core and _matches(module, FORBIDDEN_IN_PHYSICS_CORE):
                violations.append(Violation(str(rel), line, module, "physics_core_nondeterminism"))
    return violations
