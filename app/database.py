import json
from pathlib import Path
from typing import List, Optional
from models import Recipe, RecipeCreate, RecipeUpdate

BASE_DIR = Path(__file__).resolve().parent.parent
RECIPES_PATH = BASE_DIR / "recipes.json"
INVENTORY_PATH = BASE_DIR / "inventory.json"

SAMPLE_RECIPES = [
    {
        "id": 1,
        "title": "Tortilla rápida",
        "description": "Una tortilla sencilla para diario.",
        "category": "Cena",
        "servings": 2,
        "ingredients": [
            {"name": "Huevos", "amount": "4 uds"},
            {"name": "Patata", "amount": "2 uds"},
            {"name": "Sal", "amount": "1 cdita"}
        ],
        "steps": [
            "Pela y corta la patata.",
            "Fríe la patata.",
            "Mezcla con huevo batido.",
            "Cuaja la tortilla por ambos lados."
        ],
        "tags": ["rápido", "española"],
        "favorite": True,
        "planned_to_cook": False,
        "image": "https://images.unsplash.com/photo-1515516969-d4008cc6241a?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "id": 2,
        "title": "Pasta al pesto",
        "description": "Pasta fácil con salsa pesto.",
        "category": "Comida",
        "servings": 3,
        "ingredients": [
            {"name": "Pasta", "amount": "300 g"},
            {"name": "Pesto", "amount": "3 cda"}
        ],
        "steps": ["Cuece la pasta.", "Mezcla con el pesto y sirve."],
        "tags": ["italiana"],
        "favorite": False,
        "planned_to_cook": True,
        "image": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=1200&q=80"
    }
]

SAMPLE_INVENTORY = [
    {"id": 1, "name": "Huevos", "quantity": 12, "unit": "uds", "low_stock_threshold": 4, "low_stock_unit": "uds"},
    {"id": 2, "name": "Patata", "quantity": 10, "unit": "uds", "low_stock_threshold": 3, "low_stock_unit": "uds"},
    {"id": 3, "name": "Sal", "quantity": 200, "unit": "g", "low_stock_threshold": 10, "low_stock_unit": "cda"},
    {"id": 4, "name": "Pasta", "quantity": 500, "unit": "g", "low_stock_threshold": 150, "low_stock_unit": "g"},
    {"id": 5, "name": "Pesto", "quantity": 20, "unit": "g", "low_stock_threshold": 3, "low_stock_unit": "cda"}
]

RECIPE_IMAGE_MAP = {
    "tortilla": "https://images.unsplash.com/photo-1515516969-d4008cc6241a?auto=format&fit=crop&w=1200&q=80",
    "pasta": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=1200&q=80",
    "ensalada": "https://images.unsplash.com/photo-1546793665-c74683f339c1?auto=format&fit=crop&w=1200&q=80",
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=80",
    "sopa": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1200&q=80",
    "arroz": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=1200&q=80",
    "pollo": "https://images.unsplash.com/photo-1604908554165-e0b1c6f7f2e7?auto=format&fit=crop&w=1200&q=80",
}
DEFAULT_RECIPE_IMAGE = "https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=1200&q=80"

UNIT_ALIASES = {
    "gramo": "g", "gramos": "g", "g": "g",
    "kg": "kg", "kilo": "kg", "kilos": "kg",
    "ml": "ml", "mililitros": "ml",
    "l": "l", "litro": "l", "litros": "l",
    "cda": "cda", "cucharada": "cda", "cucharadas": "cda", "tbsp": "cda",
    "cdta": "cdita", "cdita": "cdita", "cucharadita": "cdita", "cucharaditas": "cdita", "tsp": "cdita",
    "ud": "uds", "uds": "uds", "unidad": "uds", "unidades": "uds", "pieza": "uds", "piezas": "uds"
}
UNIT_TO_BASE = {
    "g": ("g", 1.0), "kg": ("g", 1000.0),
    "ml": ("ml", 1.0), "l": ("ml", 1000.0),
    "cda": ("ml", 15.0), "cdita": ("ml", 5.0),
    "uds": ("uds", 1.0)
}
DENSITY_LIKE = {
    "sal": 1.22, "pesto": 0.95, "aceite": 0.91, "agua": 1.0,
    "leche": 1.03, "harina": 0.53, "azucar": 0.85, "azúcar": 0.85,
    "mantequilla": 0.96, "miel": 1.42
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _init_file(path: Path, sample: list):
    if not path.exists():
        path.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")


def init_db():
    _init_file(RECIPES_PATH, SAMPLE_RECIPES)
    _init_file(INVENTORY_PATH, SAMPLE_INVENTORY)


def _read_recipes() -> list:
    data = json.loads(RECIPES_PATH.read_text(encoding="utf-8"))
    changed = False
    for r in data:
        if "image" not in r:
            r["image"] = _pick_recipe_image(r.get("title", ""), r.get("category", ""), r.get("ingredients", []))
            changed = True
        if "favorite" not in r:
            r["favorite"] = False
            changed = True
        if "planned_to_cook" not in r:
            r["planned_to_cook"] = False
            changed = True
    if changed:
        _write_recipes(data)
    return data


def _write_recipes(data: list) -> None:
    RECIPES_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_inventory() -> list:
    data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    changed = False
    for item in data:
        if "low_stock_threshold" not in item:
            item["low_stock_threshold"] = 5
            changed = True
        if "low_stock_unit" not in item:
            item["low_stock_unit"] = item.get("unit", "uds")
            changed = True
    if changed:
        _write_inventory(data)
    return data


def _write_inventory(data: list) -> None:
    INVENTORY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _pick_recipe_image(title: str, category: str, ingredients: list) -> str:
    haystack = " ".join([title, category] + [i.get("name", "") for i in ingredients]).lower()
    for key, url in RECIPE_IMAGE_MAP.items():
        if key in haystack:
            return url
    return DEFAULT_RECIPE_IMAGE


def _normalize_unit(unit: str) -> str:
    return UNIT_ALIASES.get((unit or "").strip().lower(), (unit or "").strip().lower())


def _normalize_name(name: str) -> str:
    return (name or "").strip().lower()


def _parse_ingredient_text(name: str, amount: str) -> tuple[float, str, str]:
    amount = (amount or "").strip()
    name = (name or "").strip()
    parts = amount.split()
    if len(parts) >= 2:
        try:
            return float(parts[0].replace(",", ".")), _normalize_unit(parts[1]), name if name else " ".join(parts[2:]).strip()
        except ValueError:
            return 0.0, "", name
    if len(parts) == 1:
        try:
            return float(parts[0].replace(",", ".")), "uds", name
        except ValueError:
            return 0.0, "", name
    return 0.0, "", name


def _to_base(quantity: float, unit: str):
    norm = _normalize_unit(unit)
    if norm not in UNIT_TO_BASE:
        return None, None
    base_unit, factor = UNIT_TO_BASE[norm]
    return base_unit, quantity * factor


def _convert_between_units(name: str, required_qty: float, required_unit: str, stock_qty: float, stock_unit: str):
    req_base_unit, req_base_qty = _to_base(required_qty, required_unit)
    stock_base_unit, stock_base_qty = _to_base(stock_qty, stock_unit)
    if not req_base_unit or not stock_base_unit:
        return False, 0.0, 0.0
    if req_base_unit == stock_base_unit:
        return True, req_base_qty, stock_base_qty
    density = DENSITY_LIKE.get(_normalize_name(name))
    if not density:
        return False, 0.0, 0.0
    if req_base_unit == "ml" and stock_base_unit == "g":
        return True, req_base_qty * density, stock_base_qty
    if req_base_unit == "g" and stock_base_unit == "ml":
        return True, req_base_qty / density, stock_base_qty
    return False, 0.0, 0.0


# ── Recipe CRUD ───────────────────────────────────────────────────────────────

def list_recipes(q: Optional[str] = None) -> List[Recipe]:
    items = _read_recipes()
    if q:
        q = q.lower()
        items = [r for r in items if q in r["title"].lower() or q in r["description"].lower()]
    return [Recipe(**r) for r in items]


def get_recipe(recipe_id: int) -> Optional[Recipe]:
    for r in _read_recipes():
        if r["id"] == recipe_id:
            return Recipe(**r)
    return None


def create_recipe(payload: RecipeCreate) -> Recipe:
    items = _read_recipes()
    next_id = max([r["id"] for r in items], default=0) + 1
    record = payload.model_dump()
    record["id"] = next_id
    record["image"] = _pick_recipe_image(record.get("title", ""), record.get("category", ""), record.get("ingredients", []))
    items.append(record)
    _write_recipes(items)
    return Recipe(**record)


def update_recipe(recipe_id: int, payload: RecipeUpdate) -> Optional[Recipe]:
    items = _read_recipes()
    for i, r in enumerate(items):
        if r["id"] == recipe_id:
            record = payload.model_dump()
            record["id"] = recipe_id
            # Preserve existing image if none provided
            record["image"] = r.get("image") or _pick_recipe_image(
                record.get("title", ""), record.get("category", ""), record.get("ingredients", [])
            )
            # Preserve favorite and planned_to_cook if not in payload
            record["favorite"] = record.get("favorite", r.get("favorite", False))
            record["planned_to_cook"] = record.get("planned_to_cook", r.get("planned_to_cook", False))
            items[i] = record
            _write_recipes(items)
            return Recipe(**record)
    return None


def toggle_favorite(recipe_id: int) -> Optional[Recipe]:
    items = _read_recipes()
    for i, r in enumerate(items):
        if r["id"] == recipe_id:
            r["favorite"] = not r.get("favorite", False)
            items[i] = r
            _write_recipes(items)
            return Recipe(**r)
    return None


def toggle_planned_to_cook(recipe_id: int) -> Optional[Recipe]:
    items = _read_recipes()
    for i, r in enumerate(items):
        if r["id"] == recipe_id:
            r["planned_to_cook"] = not r.get("planned_to_cook", False)
            items[i] = r
            _write_recipes(items)
            return Recipe(**r)
    return None


def delete_recipe(recipe_id: int) -> bool:
    items = _read_recipes()
    new_items = [r for r in items if r["id"] != recipe_id]
    if len(new_items) == len(items):
        return False
    _write_recipes(new_items)
    return True


# ── Inventory CRUD ────────────────────────────────────────────────────────────

def list_inventory() -> list:
    return _read_inventory()


def create_inventory_item(name: str, quantity: float, unit: str, low_stock_threshold: float = 5, low_stock_unit: Optional[str] = None) -> dict:
    items = _read_inventory()
    next_id = max([i["id"] for i in items], default=0) + 1
    normalized_unit = _normalize_unit(unit)
    record = {
        "id": next_id,
        "name": name,
        "quantity": quantity,
        "unit": normalized_unit,
        "low_stock_threshold": low_stock_threshold,
        "low_stock_unit": _normalize_unit(low_stock_unit or normalized_unit)
    }
    items.append(record)
    _write_inventory(items)
    return record


def update_inventory_item(item_id: int, name: str, quantity: float, unit: str, low_stock_threshold: Optional[float] = None, low_stock_unit: Optional[str] = None) -> Optional[dict]:
    items = _read_inventory()
    for idx, item in enumerate(items):
        if item["id"] == item_id:
            record = {
                "id": item_id,
                "name": name,
                "quantity": quantity,
                "unit": _normalize_unit(unit),
                "low_stock_threshold": item.get("low_stock_threshold", 5) if low_stock_threshold is None else low_stock_threshold,
                "low_stock_unit": _normalize_unit(low_stock_unit or item.get("low_stock_unit", unit))
            }
            items[idx] = record
            _write_inventory(items)
            return record
    return None


def delete_inventory_item(item_id: int) -> bool:
    items = _read_inventory()
    new_items = [i for i in items if i["id"] != item_id]
    if len(new_items) == len(items):
        return False
    _write_inventory(new_items)
    return True


# ── Cooking & shopping ────────────────────────────────────────────────────────

def _compute_recipe_missing(recipe: Recipe, inventory_items: list) -> list:
    missing = []
    for ing in recipe.ingredients:
        qty, unit, resolved_name = _parse_ingredient_text(ing.name, ing.amount)
        if qty <= 0 or not resolved_name:
            continue
        stock_item = next((i for i in inventory_items if _normalize_name(i["name"]) == _normalize_name(resolved_name)), None)
        if not stock_item:
            missing.append({"name": resolved_name, "required": qty, "unit": unit, "available": 0, "recipe": recipe.title})
            continue
        convertible, required_base, available_base = _convert_between_units(
            resolved_name, qty, unit, float(stock_item["quantity"]), stock_item["unit"]
        )
        if not convertible or available_base < required_base:
            missing_amount = qty
            if convertible:
                factor = UNIT_TO_BASE[_normalize_unit(unit)][1]
                missing_amount = round((required_base - available_base) / factor, 2)
            missing.append({
                "name": resolved_name,
                "required": round(max(missing_amount, 0), 2),
                "unit": unit,
                "available": stock_item["quantity"],
                "recipe": recipe.title
            })
    return missing


def consume_ingredients_for_recipe(recipe_id: int) -> dict:
    recipe = get_recipe(recipe_id)
    if not recipe:
        return {"success": False, "error": "Receta no encontrada"}
    inv = _read_inventory()
    missing = []
    consumption_plan = []
    for ing in recipe.ingredients:
        qty, unit, resolved_name = _parse_ingredient_text(ing.name, ing.amount)
        if qty <= 0 or not resolved_name:
            continue
        stock_item = next((i for i in inv if _normalize_name(i["name"]) == _normalize_name(resolved_name)), None)
        if not stock_item:
            missing.append({"name": resolved_name, "unit": unit, "required": qty, "available": 0})
            continue
        convertible, required_base, available_base = _convert_between_units(
            resolved_name, qty, unit, float(stock_item["quantity"]), stock_item["unit"]
        )
        if not convertible:
            missing.append({"name": resolved_name, "unit": unit, "required": qty, "available": stock_item["quantity"]})
            continue
        if available_base < required_base:
            missing.append({"name": resolved_name, "unit": unit, "required": qty, "available": stock_item["quantity"]})
            continue
        consumption_plan.append({"item_id": stock_item["id"], "consume_base": required_base})
    if missing:
        return {"success": False, "missing": missing}
    for plan in consumption_plan:
        for item in inv:
            if item["id"] == plan["item_id"]:
                base_unit, base_qty = _to_base(float(item["quantity"]), item["unit"])
                new_base_qty = round(base_qty - plan["consume_base"], 2)
                factor = UNIT_TO_BASE[_normalize_unit(item["unit"])][1]
                item["quantity"] = round(new_base_qty / factor, 2)
                break
    _write_inventory(inv)
    return {"success": True, "inventory": inv}


def _is_low_stock(item: dict) -> bool:
    qty = float(item.get("quantity", 0))
    unit = item.get("unit", "")
    threshold = float(item.get("low_stock_threshold", 0))
    threshold_unit = item.get("low_stock_unit", unit)
    convertible, threshold_base, available_base = _convert_between_units(
        item.get("name", ""), threshold, threshold_unit, qty, unit
    )
    if not convertible:
        return qty <= threshold and _normalize_unit(unit) == _normalize_unit(threshold_unit)
    return available_base <= threshold_base


def list_low_stock_items() -> list:
    return [i for i in _read_inventory() if _is_low_stock(i)]


def get_shopping_list() -> dict:
    inventory_items = _read_inventory()
    low_stock = list_low_stock_items()
    planned_recipes = [Recipe(**r) for r in _read_recipes() if r.get("planned_to_cook")]
    missing_for_planned = []
    for recipe in planned_recipes:
        missing_for_planned.extend(_compute_recipe_missing(recipe, inventory_items))
    return {
        "low_stock": low_stock,
        "planned_recipes": [r.model_dump() for r in planned_recipes],
        "missing_for_planned": missing_for_planned
    }
