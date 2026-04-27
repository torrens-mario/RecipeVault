from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .database import init_db, list_recipes, get_recipe, create_recipe, update_recipe, delete_recipe, toggle_favorite, toggle_planned_to_cook, list_inventory, create_inventory_item, update_inventory_item, delete_inventory_item, consume_ingredients_for_recipe, list_low_stock_items, get_shopping_list
from .models import RecipeCreate, RecipeUpdate

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="RecipeVault")
init_db()
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request): return templates.TemplateResponse("index.html", {"request": request})
@app.get("/recipes/new", response_class=HTMLResponse)
def new_recipe_page(request: Request): return templates.TemplateResponse("recipe-form.html", {"request": request})
@app.get("/recipes/{recipe_id}", response_class=HTMLResponse)
def detail_page(request: Request, recipe_id: int): return templates.TemplateResponse("recipe-detail.html", {"request": request, "recipe_id": recipe_id})
@app.get("/shared/{recipe_id}", response_class=HTMLResponse)
def shared_recipe_page(request: Request, recipe_id: int): return templates.TemplateResponse("shared-recipe.html", {"request": request, "recipe_id": recipe_id})
@app.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request): return templates.TemplateResponse("inventory.html", {"request": request})
@app.get("/shopping-list", response_class=HTMLResponse)
def shopping_list_page(request: Request): return templates.TemplateResponse("shopping-list.html", {"request": request})

@app.get("/api/recipes")
def api_list_recipes(q: str | None = None): return [r.model_dump() for r in list_recipes(q)]
@app.get("/api/recipes/{recipe_id}")
def api_get_recipe(recipe_id: int):
    recipe = get_recipe(recipe_id)
    if not recipe: raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()
@app.post("/api/recipes", status_code=201)
def api_create_recipe(payload: RecipeCreate): return create_recipe(payload).model_dump()
@app.put("/api/recipes/{recipe_id}")
def api_update_recipe(recipe_id: int, payload: RecipeUpdate):
    recipe = update_recipe(recipe_id, payload)
    if not recipe: raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()
@app.post("/api/recipes/{recipe_id}/favorite")
def api_toggle_favorite(recipe_id: int):
    recipe = toggle_favorite(recipe_id)
    if not recipe: raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()
@app.post("/api/recipes/{recipe_id}/plan")
def api_toggle_plan(recipe_id: int):
    recipe = toggle_planned_to_cook(recipe_id)
    if not recipe: raise HTTPException(status_code=404, detail="Receta no encontrada")
    return recipe.model_dump()
@app.delete("/api/recipes/{recipe_id}", status_code=204)
def api_delete_recipe(recipe_id: int):
    ok = delete_recipe(recipe_id)
    if not ok: raise HTTPException(status_code=404, detail="Receta no encontrada")
@app.post("/api/recipes/{recipe_id}/cook")
def api_cook_recipe(recipe_id: int):
    result = consume_ingredients_for_recipe(recipe_id)
    if not result.get("success"): return JSONResponse(status_code=400, content=result)
    result["low_stock"] = list_low_stock_items(); return result
@app.get("/api/inventory")
def api_list_inventory(): return list_inventory()
@app.get("/api/inventory/low-stock")
def api_low_stock_inventory(): return list_low_stock_items()
@app.get("/api/shopping-list")
def api_shopping_list(): return get_shopping_list()
@app.post("/api/inventory", status_code=201)
def api_create_inventory_item(payload: dict):
    name = str(payload.get("name", "")).strip(); unit = str(payload.get("unit", "")).strip(); quantity = float(payload.get("quantity", 0)); threshold = float(payload.get("low_stock_threshold", 5)); threshold_unit = str(payload.get("low_stock_unit", unit)).strip()
    if not name or not unit or quantity < 0: raise HTTPException(status_code=400, detail="Datos de inventario no válidos")
    return create_inventory_item(name=name, quantity=quantity, unit=unit, low_stock_threshold=threshold, low_stock_unit=threshold_unit)
@app.put("/api/inventory/{item_id}")
def api_update_inventory_item(item_id: int, payload: dict):
    name = str(payload.get("name", "")).strip(); unit = str(payload.get("unit", "")).strip(); quantity = float(payload.get("quantity", 0)); threshold = float(payload.get("low_stock_threshold", 5)); threshold_unit = str(payload.get("low_stock_unit", unit)).strip()
    if not name or not unit or quantity < 0: raise HTTPException(status_code=400, detail="Datos de inventario no válidos")
    item = update_inventory_item(item_id=item_id, name=name, quantity=quantity, unit=unit, low_stock_threshold=threshold, low_stock_unit=threshold_unit)
    if not item: raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    return item
@app.delete("/api/inventory/{item_id}", status_code=204)
def api_delete_inventory_item(item_id: int):
    ok = delete_inventory_item(item_id)
    if not ok: raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
