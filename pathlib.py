import sys

if 'pathlib' in sys.modules:
    del sys.modules['pathlib']

_vendor_paths = [p for p in sys.path if '_vendor' in p]
for p in _vendor_paths:
    sys.path.remove(p)

import pathlib as _real_pathlib

sys.path.extend(_vendor_paths)

sys.modules['pathlib'] = _real_pathlib

for attr in dir(_real_pathlib):
    if attr.startswith('__') and attr not in ('__all__',):
        continue
    globals()[attr] = getattr(_real_pathlib, attr)
