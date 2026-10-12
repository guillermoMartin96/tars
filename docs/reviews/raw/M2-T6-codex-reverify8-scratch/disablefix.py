import ast
import os
from pathlib import Path

def replace_function(module, source, name):
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<review-disabled>', 'exec'), module.__dict__)

def pytest_collection_modifyitems(items):
    module = items[0].module
    mode = os.environ['DISABLE_FIX']
    if mode == 'F26':
        from tars.validation import m2
        source = Path('src/tars/validation/m2.py').read_text().replace('ratio = e.propellant_kg / bound if math.isfinite(bound) and bound > 0.0 else math.inf', 'ratio = e.propellant_kg / bound')
        replace_function(m2, source, 'mass_and_rocket_metrics')
    if mode == 'F27':
        source = Path('tests/test_gmat_m2.py').read_text()
        start = source.index('        def visit_ImportFrom(self, node):')
        end = source.index('    Visitor().visit', start)
        replace_function(module, source[:start] + source[end:], '_reducer_calls')
    if mode == 'F28-standalone':
        original = module._cli
        def loader():
            cli = original()
            source = Path('toolbox/scripts/gmat_m2.py').read_text()
            start = source.index('        # Every audit metric, report-only included')
            end = source.index('        missing = m2.ungated_metrics', start)
            replace_function(cli, source[:start] + source[end:], '_evaluate')
            return cli
        module._cli = loader
    if mode == 'F28-proof':
        original = module._proof_module
        def loader():
            proof = original()
            source = Path('toolbox/validators/m2_proof.py').read_text().replace('    checks.append(_exact("report_only_metrics_finite", gates.non_finite_report_only))', '')
            replace_function(proof, source, 'main')
            return proof
        module._proof_module = loader
