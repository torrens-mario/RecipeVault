import logging
import math
import os
from contextlib import asynccontextmanager
from pathlib import Path

# Debe ir antes de importar cualquier módulo de Azure
os.environ.setdefault("AZURE_LOG_LEVEL", "WARNING")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    from azure.monitor.opentelemetry import configure_azure_monitor
    configure_azure_monitor()
    # Silenciar después de configure_azure_monitor para que no lo revierta
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
    logging.getLogger("azure.monitor.opentelemetry.exporter").setLevel(logging.WARNING)
    logging.getLogger("azure.core").setLevel(logging.WARNING)
    logger.info("Azure Monitor configurado")

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from auth import create_access_token, get_current_user_id
from database import (
    authenticate_user, consume_ingredients_for_recipe, create_inventory_item,
    create_recipe, create_user, delete_inventory_item, delete_recipe,
    get_recipe, get_recipe_public, get_shopping_list, get_user_by_id,
    list_inventory, list_low_stock_items, list_recipes, toggle_favorite,
    toggle_planned_to_cook, toggle_public, update_inventory_item, update_recipe,
    update_recipe_image, init_db, seed_default_recipes, seed_default_inventory,
)
from models import RecipeCreate, RecipeUpdate, UserLogin, UserRegister
from storage import upload_recipe_image, validate_and_sanitize_image

def _parse_qty(value, default: float = 0.0) -> float:
    """Parsea un valor numérico de inventario. Rechaza inf, nan, negativos y no-numéricos."""
    try:
        v = float(value if value is not None else default)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Datos de inventario no válidos")
    if not math.isfinite(v) or v < 0:
        raise HTTPException(status_code=400, detail="Datos de inventario no válidos")
    return v


BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("RecipeVault arrancando")
    logger.info("=" * 60)
    logger.info("Tipos de log activos:")
    logger.info("  INFO    — operaciones normales: registro, login, recetas, inventario")
    logger.info("  WARNING — accesos fallidos, credenciales incorrectas, recursos no encontrados")
    logger.info("  ERROR   — fallos críticos: base de datos, excepciones no controladas")
    logger.info("=" * 60)
    try:
        init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception:
        logger.error("Error crítico al inicializar la base de datos — la app no puede arrancar")
        logger.exception("Detalle del error:")
        raise
    yield


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="RecipeVault", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))


# ── HTML pages ────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "active_page": "recipes"})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/recipes/new", response_class=HTMLResponse)
def new_recipe_page(request: Request):
    return templates.TemplateResponse("recipe-form.html", {"request": request, "active_page": "new_recipe"})

@app.get("/recipes/{recipe_id}/edit", response_class=HTMLResponse)
def edit_recipe_page(request: Request, recipe_id: int):
    return templates.TemplateResponse("recipe-form.html", {"request": request, "edit_recipe_id": recipe_id, "active_page": "recipes"})

@app.get("/recipes/{recipe_id}", response_class=HTMLResponse)
def detail_page(request: Request, recipe_id: int):
    return templates.TemplateResponse("recipe-detail.html", {"request": request, "recipe_id": recipe_id, "active_page": "recipes"})

@app.get("/shared/{recipe_id}", response_class=HTMLResponse)
def shared_recipe_page(request: Request, recipe_id: int):
    return templates.TemplateResponse("shared-recipe.html", {"request": request, "recipe_id": recipe_id})

@app.get("/api/shared/{recipe_id}")
def api_get_shared_recipe(recipe_id: int):
    recipe = get_recipe_public(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()

@app.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request, "active_page": "inventory"})

@app.get("/shopping-list", response_class=HTMLResponse)
def shopping_list_page(request: Request):
    return templates.TemplateResponse("shopping-list.html", {"request": request, "active_page": "shopping"})


# ── Auth API ──────────────────────────────────────────────────────────────────

@app.post("/api/auth/register", status_code=201)
@limiter.limit("5/minute")
def api_register(request: Request, payload: UserRegister):
    user = create_user(payload.username, payload.email, payload.password)
    if not user:
        logger.warning("Intento de registro fallido — usuario o email ya existe: %s", payload.email)
        raise HTTPException(status_code=400, detail="El usuario o email ya existe")
    seed_default_recipes(user["id"])
    seed_default_inventory(user["id"])
    token = create_access_token(user["id"])
    logger.info("Nuevo usuario registrado: %s (id=%s)", payload.username, user["id"])
    return {"access_token": token, "token_type": "bearer", "user_id": user["id"], "username": user["username"]}

@app.post("/api/auth/login")
@limiter.limit("10/minute")
def api_login(request: Request, payload: UserLogin):
    user = authenticate_user(payload.email, payload.password)
    if not user:
        logger.warning("Intento de login fallido para: %s", payload.email)
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    token = create_access_token(user["id"])
    logger.info("Login correcto: %s (id=%s)", user["username"], user["id"])
    return {"access_token": token, "token_type": "bearer", "user_id": user["id"], "username": user["username"]}

@app.get("/api/auth/me")
def api_me(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ── Recipe API ────────────────────────────────────────────────────────────────

@app.get("/api/recipes")
def api_list_recipes(q: str | None = None, user_id: int = Depends(get_current_user_id)):
    return [r.model_dump() for r in list_recipes(user_id=user_id, q=q)]

@app.get("/api/recipes/{recipe_id}")
def api_get_recipe(recipe_id: int, user_id: int = Depends(get_current_user_id)):
    recipe = get_recipe(recipe_id, user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()

@app.post("/api/recipes", status_code=201)
def api_create_recipe(payload: RecipeCreate, user_id: int = Depends(get_current_user_id)):
    recipe = create_recipe(payload, user_id)
    logger.info("Receta creada: '%s' (id=%s, user=%s)", recipe.title, recipe.id, user_id)
    return recipe.model_dump()

@app.put("/api/recipes/{recipe_id}")
def api_update_recipe(recipe_id: int, payload: RecipeUpdate, user_id: int = Depends(get_current_user_id)):
    recipe = update_recipe(recipe_id, payload, user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()

@app.post("/api/recipes/{recipe_id}/image")
async def api_upload_recipe_image(
    recipe_id: int,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    recipe = get_recipe(recipe_id, user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    data = await file.read()
    try:
        clean_data = validate_and_sanitize_image(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        image_url = upload_recipe_image(clean_data)
    except Exception as e:
        logger.error("Error al subir imagen a Azure Storage: %s", e)
        raise HTTPException(status_code=503, detail="Error al subir la imagen. Inténtalo de nuevo.")
    updated = update_recipe_image(recipe_id, user_id, image_url)
    logger.info("Imagen de receta actualizada: id=%s (user=%s)", recipe_id, user_id)
    return {"image_url": updated.image if updated else image_url}

@app.post("/api/recipes/{recipe_id}/favorite")
def api_toggle_favorite(recipe_id: int, user_id: int = Depends(get_current_user_id)):
    recipe = toggle_favorite(recipe_id, user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()

@app.post("/api/recipes/{recipe_id}/plan")
def api_toggle_plan(recipe_id: int, user_id: int = Depends(get_current_user_id)):
    recipe = toggle_planned_to_cook(recipe_id, user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()

@app.delete("/api/recipes/{recipe_id}", status_code=204)
def api_delete_recipe(recipe_id: int, user_id: int = Depends(get_current_user_id)):
    if not delete_recipe(recipe_id, user_id):
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    logger.info("Receta eliminada: id=%s (user=%s)", recipe_id, user_id)

@app.post("/api/recipes/{recipe_id}/public")
def api_toggle_public(recipe_id: int, user_id: int = Depends(get_current_user_id)):
    recipe = toggle_public(recipe_id, user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()

@app.post("/api/recipes/{recipe_id}/cook")
def api_cook_recipe(recipe_id: int, user_id: int = Depends(get_current_user_id)):
    result = consume_ingredients_for_recipe(recipe_id, user_id)
    if not result.get("success"):
        logger.warning("Cocinar receta id=%s fallido (user=%s): ingredientes insuficientes", recipe_id, user_id)
        return JSONResponse(status_code=400, content=result)
    logger.info("Receta cocinada: id=%s (user=%s)", recipe_id, user_id)
    result["low_stock"] = list_low_stock_items(user_id)
    return result


# ── Inventory API ─────────────────────────────────────────────────────────────

@app.get("/api/inventory")
def api_list_inventory(user_id: int = Depends(get_current_user_id)):
    return list_inventory(user_id)

@app.get("/api/inventory/low-stock")
def api_low_stock_inventory(user_id: int = Depends(get_current_user_id)):
    return list_low_stock_items(user_id)

@app.get("/api/shopping-list")
def api_shopping_list(user_id: int = Depends(get_current_user_id)):
    return get_shopping_list(user_id)

@app.post("/api/inventory", status_code=201)
def api_create_inventory_item(payload: dict, user_id: int = Depends(get_current_user_id)):
    name = str(payload.get("name", "")).strip()
    unit = str(payload.get("unit", "")).strip()
    quantity = _parse_qty(payload.get("quantity", 0))
    threshold = _parse_qty(payload.get("low_stock_threshold", 5))
    threshold_unit = str(payload.get("low_stock_unit", unit)).strip()
    if not name or not unit or len(name) > 100:
        raise HTTPException(status_code=400, detail="Datos de inventario no válidos")
    item = create_inventory_item(
        user_id=user_id, name=name, quantity=quantity, unit=unit,
        low_stock_threshold=threshold, low_stock_unit=threshold_unit,
    )
    logger.info("Ingrediente añadido al inventario: '%s' %s %s (user=%s)", name, quantity, unit, user_id)
    return item

@app.put("/api/inventory/{item_id}")
def api_update_inventory_item(item_id: int, payload: dict, user_id: int = Depends(get_current_user_id)):
    name = str(payload.get("name", "")).strip()
    unit = str(payload.get("unit", "")).strip()
    quantity = _parse_qty(payload.get("quantity", 0))
    threshold = _parse_qty(payload.get("low_stock_threshold", 5))
    threshold_unit = str(payload.get("low_stock_unit", unit)).strip()
    if not name or not unit or len(name) > 100:
        logger.warning("Datos de inventario no válidos — user=%s payload=%s", user_id, payload)
        raise HTTPException(status_code=400, detail="Datos de inventario no válidos")
    item = update_inventory_item(
        item_id=item_id, user_id=user_id, name=name, quantity=quantity,
        unit=unit, low_stock_threshold=threshold, low_stock_unit=threshold_unit,
    )
    if not item:
        logger.error("Ingrediente id=%s no encontrado al actualizar (user=%s)", item_id, user_id)
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return item

@app.delete("/api/inventory/{item_id}", status_code=204)
def api_delete_inventory_item(item_id: int, user_id: int = Depends(get_current_user_id)):
    if not delete_inventory_item(item_id, user_id):
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
