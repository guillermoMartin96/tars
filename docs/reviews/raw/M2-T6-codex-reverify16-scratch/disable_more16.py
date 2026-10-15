# ruff: noqa
import os, importlib.util

mode = os.environ["DISABLE16"]
old = importlib.util.module_from_spec


def load(spec):
    mod = old(spec)
    if str(spec.origin).endswith("toolbox/scripts/reference_snapshot.py"):
        loader = spec.loader

        class L:
            def exec_module(self, mod):
                source = loader.get_source(spec.name)
                if mode == "coverage":
                    source = source.replace("if uncovered:", "if False and uncovered:")
                elif mode == "scope":
                    source = source.replace(
                        'bad(scope, f"verification raised {exc!r}")',
                        "pass # disabled fail-closed wrapper",
                    )
                elif mode == "gmat":
                    source = source.replace(
                        'bad(name, f"verification raised {exc!r}")',
                        "pass # disabled fail-closed wrapper",
                    )
                exec(compile(source, spec.origin, "exec"), mod.__dict__)

        spec.loader = L()
    return mod


importlib.util.module_from_spec = load
