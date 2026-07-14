import os
import importlib.util
import pathlib
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='API')
# CRUD generico server-side (persistencia multi-dispositivo)
try:
    from app.routers import data as _data_router
    app.include_router(_data_router.router)
except Exception as _e:
    import logging; logging.getLogger('uvicorn').warning('data router: %s', _e)

origins = os.environ.get('CORS_ORIGINS', '*').split(',')
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=['*'], allow_headers=['*'])

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/')
def root():
    return {'service': 'api', 'status': 'ok'}

# Auto-incluir routers escaneando el FILESYSTEM (no requiere __init__.py).
# Carga cada .py bajo app/ que defina `router = APIRouter()`.
def _autoload_routers():
    base = pathlib.Path(__file__).parent
    app_dir = base / 'app'
    if not app_dir.is_dir():
        return
    import sys
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))
    for py in sorted(app_dir.rglob('*.py')):
        if py.name.startswith('test') or '__pycache__' in str(py):
            continue
        try:
            txt = py.read_text(encoding='utf-8')
        except Exception:
            continue
        if 'APIRouter' not in txt or 'router' not in txt:
            continue
        modname = 'autoload_' + py.stem + '_' + str(abs(hash(str(py))) % 100000)
        try:
            spec = importlib.util.spec_from_file_location(modname, py)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception:
            continue
        r = getattr(mod, 'router', None)
        if isinstance(r, APIRouter):
            try:
                app.include_router(r)
            except Exception:
                pass

_autoload_routers()
