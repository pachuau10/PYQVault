import sys
import importlib.util
import importlib.machinery

if 'pathlib' in sys.modules:
    del sys.modules['pathlib']

project_root = __file__.rsplit('/', 1)[0] if '/' in __file__ else '.'
cleaned_path = [p for p in sys.path if p != project_root and '_vendor' not in p]

finder = importlib.machinery.PathFinder()
spec = finder.find_spec('pathlib', cleaned_path)
if spec and spec.origin:
    stdlib_pathlib = importlib.util.module_from_spec(spec)
    sys.modules['pathlib'] = stdlib_pathlib
    spec.loader.exec_module(stdlib_pathlib)
    for attr in dir(stdlib_pathlib):
        if attr.startswith('__') and attr not in ('__all__',):
            continue
        globals()[attr] = getattr(stdlib_pathlib, attr)
