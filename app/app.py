from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth import create_access_token, get_current_user_id
from database import (
    authenticate_user, consume_ingredients_for_recipe, create_inventory_item,
    create_recipe, create_user, delete_inventory_item, delete_recipe,
    get_recipe, get_recipe_public, get_shopping_list, get_user_by_id,
    list_inventory, list_low_stock_items, list_recipes, toggle_favorite,
    toggle_planned_to_cook, update_inventory_item, update_recipe,
    update_recipe_image, init_db,
)
from models import RecipeCreate, RecipeUpdate, UserLogin, UserRegister
from storage import upload_recipe_image

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="RecipeVault")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))


@app.on_event("startup")
def startup():
    init_db()


# ── HTML pages ────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/recipes/new", response_class=HTMLResponse)
def new_recipe_page(request: Request):
    return templates.TemplateResponse("recipe-form.html", {"request": request})

@app.get("/recipes/{recipe_id}/edit", response_class=HTMLResponse)
def edit_recipe_page(request: Request, recipe_id: int):
    return templates.TemplateResponse("recipe-form.html", {"request": request, "edit_recipe_id": recipe_id})

@app.get("/recipes/{recipe_id}", response_class=HTMLResponse)
def detail_page(request: Request, recipe_id: int):
    return templates.TemplateResponse("recipe-detail.html", {"request": request, "recipe_id": recipe_id})

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
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.get("/shopping-list", response_class=HTMLResponse)
def shopping_list_page(request: Request):
    return templates.TemplateResponse("shopping-list.html", {"request": request})


# ── Auth API ──────────────────────────────────────────────────────────────────

@app.post("/api/auth/register", status_code=201)
def api_register(payload: UserRegister):
    user = create_user(payload.username, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario o email ya existe")
    token = create_access_token(user["id"])
    return {"access_token": token, "token_type": "bearer", "user_id": user["id"], "username": user["username"]}

@app.post("/api/auth/login")
def api_login(payload: UserLogin):
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    token = create_access_token(user["id"])
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
    return create_recipe(payload, user_id).model_dump()

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
    image_url = upload_recipe_image(data, file.content_type or "image/jpeg")
    updated = update_recipe_image(recipe_id, user_id, image_url)
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

@app.post("/api/recipes/{recipe_id}/cook")
def api_cook_recipe(recipe_id: int, user_id: int = Depends(get_current_user_id)):
    result = consume_ingredients_for_recipe(recipe_id, user_id)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
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
    quantity = float(payload.get("quantity", 0))
    threshold = float(payload.get("low_stock_threshold", 5))
    threshold_unit = str(payload.get("low_stock_unit", unit)).strip()
    if not name or not unit or quantity < 0:
        raise HTTPException(status_code=400, detail="Datos de inventario no válidos")
    return create_inventory_item(
        user_id=user_id, name=name, quantity=quantity, unit=unit,
        low_stock_threshold=threshold, low_stock_unit=threshold_unit,
    )

@app.put("/api/inventory/{item_id}")
def api_update_inventory_item(item_id: int, payload: dict, user_id: int = Depends(get_current_user_id)):
    name = str(payload.get("name", "")).strip()
    unit = str(payload.get("unit", "")).strip()
    quantity = float(payload.get("quantity", 0))
    threshold = float(payload.get("low_stock_threshold", 5))
    threshold_unit = str(payload.get("low_stock_unit", unit)).strip()
    if not name or not unit or quantity < 0:
        raise HTTPException(status_code=400, detail="Datos de inventario no válidos")
    item = update_inventory_item(
        item_id=item_id, user_id=user_id, name=name, quantity=quantity,
        unit=unit, low_stock_threshold=threshold, low_stock_unit=threshold_unit,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return item

@app.delete("/api/inventory/{item_id}", status_code=204)
def api_delete_inventory_item(item_id: int, user_id: int = Depends(get_current_user_id)):
    if not delete_inventory_item(item_id, user_id):
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
