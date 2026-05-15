import sys
import os
 
# Oryx extrae el build a /tmp/<hash>/ en cada deploy.
# Buscamos esa carpeta dinámicamente y la añadimos al path
# para que 'backend' sea importable.
_tmp = '/tmp'
for _d in os.listdir(_tmp):
    _full = os.path.join(_tmp, _d)
    if os.path.isdir(_full) and os.path.exists(os.path.join(_full, 'backend')):
        if _full not in sys.path:
            sys.path.insert(0, _full)
        break
 
from backend.main import app