"""Interactive tutorials, one module per spec item (te1.py, vd1.py, ...).

Each module defines TUTORIAL = {"minutes": int, "blocks": [...]}, where each
block is a dict with the fields of curriculum.models.TutorialBlock. Widgets
named in blocks are registered in static/js/widgets/<code>.js.

`python manage.py check_tutorials` validates every module.
"""

import importlib
import pkgutil


def load_all():
    """{spec item code: TUTORIAL dict} for every module in this package."""
    out = {}
    for mod in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{mod.name}")
        if hasattr(module, "TUTORIAL"):
            out[mod.name.upper()] = module.TUTORIAL
    return out
