import sys

vendor_paths = [p for p in sys.path if '_vendor' in p]
for p in vendor_paths:
    if p in sys.path:
        sys.path.remove(p)

import pathlib

sys.path = list(sys.path) + vendor_paths
