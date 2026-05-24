import os
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine, or_, func
from sqlalchemy.orm import sessionmaker

from auth import hash_password, verify_password
from db_models import Base, InventoryItem as InventoryItemModel, Recipe as RecipeModel, User as UserModel
from models import Recipe, RecipeCreate, RecipeUpdate

# ── Engine ─────────────────────────────────────────────────────────────────────

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        url = os.environ["DATABASE_URL"]
        _engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


@contextmanager
def _db():
    _get_engine()
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    engine = _get_engine()
    Base.metadata.create_all(bind=engine)


# ── Unit conversion (unchanged logic) ─────────────────────────────────────────

RECIPE_IMAGE_MAP = {
    "tortilla": "https://images.unsplash.com/photo-1515516969-d4008cc6241a?auto=format&fit=crop&w=1200&q=80",
    "pasta": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=1200&q=80",
    "ensalada": "https://images.unsplash.com/photo-1546793665-c74683f339c1?auto=format&fit=crop&w=1200&q=80",
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=80",
    "sopa": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1200&q=80",
    "arroz": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=1200&q=80",
    "pollo": "https://images.unsplash.com/photo-1604908554165-e0b1c6f7f2e7?auto=format&fit=crop&w=1200&q=80",
    "paella": "https://images.unsplash.com/photo-1534080564583-6be75777b70a?auto=format&fit=crop&w=1200&q=80",
    "hamburguesa": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1200&q=80",
    "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1200&q=80",
    "sushi": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?auto=format&fit=crop&w=1200&q=80",
    "tacos": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=1200&q=80",
    "taco": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=1200&q=80",
    "curry": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=1200&q=80",
    "salmon": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=1200&q=80",
    "salmón": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=1200&q=80",
    "atun": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=1200&q=80",
    "atún": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=1200&q=80",
    "pescado": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=1200&q=80",
    "gambas": "https://images.unsplash.com/photo-1565958011703-44f9829ba187?auto=format&fit=crop&w=1200&q=80",
    "marisco": "https://images.unsplash.com/photo-1565958011703-44f9829ba187?auto=format&fit=crop&w=1200&q=80",
    "carne": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=1200&q=80",
    "ternera": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=1200&q=80",
    "cerdo": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=1200&q=80",
    "lasaña": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=1200&q=80",
    "ramen": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=1200&q=80",
    "wok": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=1200&q=80",
    "tarta": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=1200&q=80",
    "pastel": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=1200&q=80",
    "bizcocho": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=1200&q=80",
    "chocolate": "https://images.unsplash.com/photo-1606312619070-d48b6b3b9f1c?auto=format&fit=crop&w=1200&q=80",
    "pan": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1200&q=80",
    "galleta": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=1200&q=80",
    "helado": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=1200&q=80",
    "batido": "https://images.unsplash.com/photo-1505252585461-04db1eb84625?auto=format&fit=crop&w=1200&q=80",
    "smoothie": "https://images.unsplash.com/photo-1505252585461-04db1eb84625?auto=format&fit=crop&w=1200&q=80",
    "verduras": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=80",
    "vegetariana": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=80",
    "gazpacho": "https://images.unsplash.com/photo-1586808214612-d6b9c09c8b1e?auto=format&fit=crop&w=1200&q=80",
    "caldo": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1200&q=80",
    "croqueta": "https://images.unsplash.com/photo-1574484284002-952d92456975?auto=format&fit=crop&w=1200&q=80",
    "huevo": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1200&q=80",
    "risotto": "https://images.unsplash.com/photo-1476124369491-e7addf5db371?auto=format&fit=crop&w=1200&q=80",
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


def _pick_recipe_image(title: str, category: str, ingredients: list) -> str:
    haystack = " ".join([title, category] + [i.get("name", "") if isinstance(i, dict) else i for i in ingredients]).lower()
    for key, url in RECIPE_IMAGE_MAP.items():
        if key in haystack:
            return url
    return DEFAULT_RECIPE_IMAGE


def _normalize_unit(unit: str) -> str:
    return UNIT_ALIASES.get((unit or "").strip().lower(), (unit or "").strip().lower())


def _normalize_name(name: str) -> str:
    return (name or "").strip().lower()


def _parse_ingredient_text(name: str, amount: str):
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


def _recipe_row_to_model(row: RecipeModel) -> Recipe:
    return Recipe(
        id=row.id,
        title=row.title,
        description=row.description or "",
        category=row.category or "",
        servings=row.servings or 1,
        ingredients=row.ingredients or [],
        steps=row.steps or [],
        tags=row.tags or [],
        favorite=row.favorite or False,
        planned_to_cook=row.planned_to_cook or False,
        is_public=row.is_public if row.is_public is not None else True,
        image=row.image or "",
        prep_time=row.prep_time or 0,
        cook_time=row.cook_time or 0,
        difficulty=row.difficulty or "Media",
        notes=row.notes or "",
        rating=row.rating or 0,
    )


def _inventory_row_to_dict(row: InventoryItemModel) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "quantity": row.quantity,
        "unit": row.unit,
        "low_stock_threshold": row.low_stock_threshold,
        "low_stock_unit": row.low_stock_unit,
    }


# ── User CRUD ──────────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password: str) -> Optional[dict]:
    with _db() as db:
        if db.query(UserModel).filter(
            or_(UserModel.username == username, UserModel.email == email)
        ).first():
            return None
        user = UserModel(
            username=username,
            email=email,
            hashed_password=hash_password(password),
        )
        db.add(user)
        db.flush()
        return {"id": user.id, "username": user.username, "email": user.email}


def authenticate_user(email: str, password: str) -> Optional[dict]:
    with _db() as db:
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return {"id": user.id, "username": user.username, "email": user.email}


def get_user_by_id(user_id: int) -> Optional[dict]:
    with _db() as db:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None
        return {"id": user.id, "username": user.username, "email": user.email}


# ── Recipe CRUD ────────────────────────────────────────────────────────────────

def list_recipes(user_id: int, q: Optional[str] = None):
    with _db() as db:
        query = db.query(RecipeModel).filter(RecipeModel.user_id == user_id)
        if q:
            ql = f"%{q.lower()}%"
            query = query.filter(
                or_(
                    func.lower(RecipeModel.title).like(ql),
                    func.lower(RecipeModel.description).like(ql),
                )
            )
        rows = query.order_by(RecipeModel.created_at.desc()).all()
        return [_recipe_row_to_model(r) for r in rows]


def get_recipe_public(recipe_id: int) -> Optional[Recipe]:
    with _db() as db:
        row = db.query(RecipeModel).filter(
            RecipeModel.id == recipe_id,
            RecipeModel.is_public.is_(True),
        ).first()
        return _recipe_row_to_model(row) if row else None


def toggle_public(recipe_id: int, user_id: int) -> Optional[Recipe]:
    with _db() as db:
        row = db.query(RecipeModel).filter(
            RecipeModel.id == recipe_id, RecipeModel.user_id == user_id
        ).first()
        if not row:
            return None
        current = row.is_public if row.is_public is not None else True
        row.is_public = not current
        return _recipe_row_to_model(row)


def get_recipe(recipe_id: int, user_id: int) -> Optional[Recipe]:
    with _db() as db:
        row = db.query(RecipeModel).filter(
            RecipeModel.id == recipe_id, RecipeModel.user_id == user_id
        ).first()
        return _recipe_row_to_model(row) if row else None


def create_recipe(payload: RecipeCreate, user_id: int) -> Recipe:
    data = payload.model_dump()
    image = data.get("image") or _pick_recipe_image(
        data.get("title", ""), data.get("category", ""), data.get("ingredients", [])
    )
    with _db() as db:
        row = RecipeModel(user_id=user_id, **{**data, "image": image})
        db.add(row)
        db.flush()
        return _recipe_row_to_model(row)


def update_recipe(recipe_id: int, payload: RecipeUpdate, user_id: int) -> Optional[Recipe]:
    with _db() as db:
        row = db.query(RecipeModel).filter(
            RecipeModel.id == recipe_id, RecipeModel.user_id == user_id
        ).first()
        if not row:
            return None
        data = payload.model_dump()
        for field, value in data.items():
            if field == "image":
                continue
            if value is not None or field in ("favorite", "planned_to_cook", "is_public"):
                setattr(row, field, value)
        if not row.image:
            row.image = _pick_recipe_image(row.title or "", row.category or "", row.ingredients or [])
        return _recipe_row_to_model(row)


def update_recipe_image(recipe_id: int, user_id: int, image_url: str) -> Optional[Recipe]:
    with _db() as db:
        row = db.query(RecipeModel).filter(
            RecipeModel.id == recipe_id, RecipeModel.user_id == user_id
        ).first()
        if not row:
            return None
        row.image = image_url
        return _recipe_row_to_model(row)


def toggle_favorite(recipe_id: int, user_id: int) -> Optional[Recipe]:
    with _db() as db:
        row = db.query(RecipeModel).filter(
            RecipeModel.id == recipe_id, RecipeModel.user_id == user_id
        ).first()
        if not row:
            return None
        row.favorite = not row.favorite
        return _recipe_row_to_model(row)


def toggle_planned_to_cook(recipe_id: int, user_id: int) -> Optional[Recipe]:
    with _db() as db:
        row = db.query(RecipeModel).filter(
            RecipeModel.id == recipe_id, RecipeModel.user_id == user_id
        ).first()
        if not row:
            return None
        row.planned_to_cook = not row.planned_to_cook
        return _recipe_row_to_model(row)


def delete_recipe(recipe_id: int, user_id: int) -> bool:
    with _db() as db:
        row = db.query(RecipeModel).filter(
            RecipeModel.id == recipe_id, RecipeModel.user_id == user_id
        ).first()
        if not row:
            return False
        db.delete(row)
        return True


# ── Seed data ─────────────────────────────────────────────────────────────────

_DEFAULT_RECIPES = [
    {
        "title": "Tortilla española",
        "description": "La clásica tortilla de patatas, jugosa por dentro y dorada por fuera.",
        "category": "Española",
        "servings": 4,
        "prep_time": 15,
        "cook_time": 25,
        "difficulty": "Media",
        "rating": 5.0,
        "favorite": True,
        "planned_to_cook": False,
        "tags": ["española", "clásica", "huevo"],
        "notes": "El truco está en dejarla jugosa por dentro. Usa bastante aceite para freír las patatas.",
        "ingredients": [
            {"name": "Huevos", "amount": "6 uds"},
            {"name": "Patata", "amount": "500 g"},
            {"name": "Cebolla", "amount": "1 uds"},
            {"name": "Aceite de oliva", "amount": "100 ml"},
            {"name": "Sal", "amount": "1 cdita"},
        ],
        "steps": [
            "Pela y corta las patatas en láminas finas. Pica la cebolla.",
            "Fríe las patatas y la cebolla en aceite a fuego medio durante 20 minutos.",
            "Escurre el aceite. Bate los huevos con sal y mezcla con las patatas.",
            "Cuaja la tortilla en una sartén con un poco de aceite a fuego medio.",
            "Dale la vuelta con un plato y cocina 2-3 minutos más.",
        ],
    },
    {
        "title": "Pasta carbonara",
        "description": "Pasta cremosa con panceta, huevo y queso parmesano. Sin nata, como en Roma.",
        "category": "Italiana",
        "servings": 2,
        "prep_time": 5,
        "cook_time": 20,
        "difficulty": "Media",
        "rating": 5.0,
        "favorite": True,
        "planned_to_cook": False,
        "tags": ["pasta", "italiana", "rápida"],
        "notes": "Lo más importante: mezclar fuera del fuego para que el huevo no se cuaje.",
        "ingredients": [
            {"name": "Pasta", "amount": "200 g"},
            {"name": "Panceta", "amount": "100 g"},
            {"name": "Huevos", "amount": "2 uds"},
            {"name": "Queso parmesano", "amount": "50 g"},
            {"name": "Pimienta negra", "amount": "1 cdita"},
            {"name": "Sal", "amount": "1 cdita"},
        ],
        "steps": [
            "Cuece la pasta en agua con sal hasta que esté al dente.",
            "Fríe la panceta en una sartén sin aceite hasta que quede crujiente.",
            "Mezcla los huevos con el queso rallado y la pimienta en un bol.",
            "Escurre la pasta (guarda un poco del agua). Apaga el fuego y mezcla con la panceta.",
            "Añade la mezcla de huevo y remueve rápido. Usa el agua de la pasta para ajustar la cremosidad.",
        ],
    },
    {
        "title": "Pollo al horno con patatas",
        "description": "Pollo jugoso con patatas doradas al horno, con ajo y romero.",
        "category": "Carnes",
        "servings": 4,
        "prep_time": 15,
        "cook_time": 60,
        "difficulty": "Fácil",
        "rating": 4.0,
        "favorite": False,
        "planned_to_cook": True,
        "tags": ["pollo", "horno", "familiar"],
        "notes": "",
        "ingredients": [
            {"name": "Pollo", "amount": "1 uds"},
            {"name": "Patata", "amount": "800 g"},
            {"name": "Ajo", "amount": "4 uds"},
            {"name": "Aceite de oliva", "amount": "3 cda"},
            {"name": "Sal", "amount": "1 cdita"},
            {"name": "Romero", "amount": "2 cdita"},
        ],
        "steps": [
            "Precalienta el horno a 200°C.",
            "Trocea el pollo y corta las patatas en gajos. Colócalos en una bandeja.",
            "Aliña con aceite, ajo machacado, sal y romero. Mezcla bien.",
            "Hornea 60 minutos, dando la vuelta a mitad de cocción.",
        ],
    },
    {
        "title": "Gazpacho andaluz",
        "description": "Sopa fría de tomate perfecta para el verano. Refrescante y muy saludable.",
        "category": "Sopas",
        "servings": 4,
        "prep_time": 15,
        "cook_time": 0,
        "difficulty": "Fácil",
        "rating": 4.0,
        "favorite": False,
        "planned_to_cook": False,
        "tags": ["gazpacho", "frío", "verano", "vegetariano"],
        "notes": "Mejor prepararlo de un día para otro para que los sabores se integren.",
        "ingredients": [
            {"name": "Tomate", "amount": "1 kg"},
            {"name": "Pepino", "amount": "1 uds"},
            {"name": "Pimiento verde", "amount": "1 uds"},
            {"name": "Ajo", "amount": "1 uds"},
            {"name": "Aceite de oliva", "amount": "3 cda"},
            {"name": "Vinagre", "amount": "1 cda"},
            {"name": "Sal", "amount": "1 cdita"},
            {"name": "Pan", "amount": "50 g"},
        ],
        "steps": [
            "Trocea todos los ingredientes y ponlos en el vaso de la batidora.",
            "Añade el pan remojado en agua, aceite, vinagre y sal.",
            "Bate todo hasta obtener una textura suave. Cuela si quieres más fino.",
            "Enfría en la nevera al menos 1 hora antes de servir.",
        ],
    },
    {
        "title": "Ensalada César",
        "description": "La ensalada más famosa del mundo, con lechuga romana, picatostes y aderezo César.",
        "category": "Ensaladas",
        "servings": 2,
        "prep_time": 15,
        "cook_time": 5,
        "difficulty": "Fácil",
        "rating": 4.0,
        "favorite": False,
        "planned_to_cook": False,
        "tags": ["ensalada", "ligera"],
        "notes": "Para la salsa auténtica, añade anchoas y mostaza de Dijon.",
        "ingredients": [
            {"name": "Lechuga romana", "amount": "1 uds"},
            {"name": "Pan", "amount": "2 uds"},
            {"name": "Queso parmesano", "amount": "30 g"},
            {"name": "Aceite de oliva", "amount": "2 cda"},
            {"name": "Limón", "amount": "1 uds"},
            {"name": "Ajo", "amount": "1 uds"},
        ],
        "steps": [
            "Corta el pan en dados y tuéstalos con aceite y ajo en la sartén hasta que queden crujientes.",
            "Lava y trocea la lechuga en trozos grandes.",
            "Prepara el aderezo mezclando aceite, zumo de limón, ajo y sal.",
            "Mezcla todo en un bol grande y añade el queso rallado por encima.",
        ],
    },
]

_DEFAULT_INVENTORY = [
    {"name": "Aceite de oliva", "quantity": 750, "unit": "ml", "low_stock_threshold": 200, "low_stock_unit": "ml"},
    {"name": "Sal", "quantity": 500, "unit": "g", "low_stock_threshold": 100, "low_stock_unit": "g"},
    {"name": "Huevos", "quantity": 6, "unit": "uds", "low_stock_threshold": 2, "low_stock_unit": "uds"},
    {"name": "Leche", "quantity": 1000, "unit": "ml", "low_stock_threshold": 500, "low_stock_unit": "ml"},
    {"name": "Harina", "quantity": 1000, "unit": "g", "low_stock_threshold": 200, "low_stock_unit": "g"},
    {"name": "Azúcar", "quantity": 500, "unit": "g", "low_stock_threshold": 100, "low_stock_unit": "g"},
    {"name": "Pasta", "quantity": 500, "unit": "g", "low_stock_threshold": 100, "low_stock_unit": "g"},
    {"name": "Arroz", "quantity": 1000, "unit": "g", "low_stock_threshold": 200, "low_stock_unit": "g"},
    {"name": "Patata", "quantity": 1000, "unit": "g", "low_stock_threshold": 300, "low_stock_unit": "g"},
    {"name": "Cebolla", "quantity": 3, "unit": "uds", "low_stock_threshold": 1, "low_stock_unit": "uds"},
    {"name": "Ajo", "quantity": 2, "unit": "uds", "low_stock_threshold": 1, "low_stock_unit": "uds"},
    {"name": "Tomate", "quantity": 4, "unit": "uds", "low_stock_threshold": 1, "low_stock_unit": "uds"},
    {"name": "Zanahoria", "quantity": 3, "unit": "uds", "low_stock_threshold": 1, "low_stock_unit": "uds"},
    {"name": "Mantequilla", "quantity": 200, "unit": "g", "low_stock_threshold": 50, "low_stock_unit": "g"},
    {"name": "Queso", "quantity": 200, "unit": "g", "low_stock_threshold": 50, "low_stock_unit": "g"},
]


def seed_default_recipes(user_id: int):
    with _db() as db:
        if db.query(RecipeModel).filter(RecipeModel.user_id == user_id).first():
            return
        for data in _DEFAULT_RECIPES:
            image = _pick_recipe_image(data.get("title", ""), data.get("category", ""), data.get("ingredients", []))
            row = RecipeModel(user_id=user_id, image=image, **data)
            db.add(row)


def seed_default_inventory(user_id: int):
    with _db() as db:
        if db.query(InventoryItemModel).filter(InventoryItemModel.user_id == user_id).first():
            return
        for data in _DEFAULT_INVENTORY:
            row = InventoryItemModel(user_id=user_id, **data)
            db.add(row)


# ── Inventory CRUD ─────────────────────────────────────────────────────────────

def list_inventory(user_id: int) -> list:
    with _db() as db:
        rows = db.query(InventoryItemModel).filter(
            InventoryItemModel.user_id == user_id
        ).order_by(InventoryItemModel.name).all()
        return [_inventory_row_to_dict(r) for r in rows]


def create_inventory_item(
    user_id: int, name: str, quantity: float, unit: str,
    low_stock_threshold: float = 5, low_stock_unit: Optional[str] = None
) -> dict:
    normalized_unit = _normalize_unit(unit)
    with _db() as db:
        row = InventoryItemModel(
            user_id=user_id,
            name=name,
            quantity=quantity,
            unit=normalized_unit,
            low_stock_threshold=low_stock_threshold,
            low_stock_unit=_normalize_unit(low_stock_unit or normalized_unit),
        )
        db.add(row)
        db.flush()
        return _inventory_row_to_dict(row)


def update_inventory_item(
    item_id: int, user_id: int, name: str, quantity: float, unit: str,
    low_stock_threshold: Optional[float] = None, low_stock_unit: Optional[str] = None
) -> Optional[dict]:
    with _db() as db:
        row = db.query(InventoryItemModel).filter(
            InventoryItemModel.id == item_id, InventoryItemModel.user_id == user_id
        ).first()
        if not row:
            return None
        row.name = name
        row.quantity = quantity
        row.unit = _normalize_unit(unit)
        if low_stock_threshold is not None:
            row.low_stock_threshold = low_stock_threshold
        if low_stock_unit is not None:
            row.low_stock_unit = _normalize_unit(low_stock_unit)
        return _inventory_row_to_dict(row)


def delete_inventory_item(item_id: int, user_id: int) -> bool:
    with _db() as db:
        row = db.query(InventoryItemModel).filter(
            InventoryItemModel.id == item_id, InventoryItemModel.user_id == user_id
        ).first()
        if not row:
            return False
        db.delete(row)
        return True


# ── Cooking & shopping ─────────────────────────────────────────────────────────

def _compute_recipe_missing(recipe: Recipe, inventory_items: list) -> list:
    missing = []
    for ing in recipe.ingredients:
        qty, unit, resolved_name = _parse_ingredient_text(ing.name, ing.amount)
        if qty <= 0 or not resolved_name:
            continue
        stock_item = next(
            (i for i in inventory_items if _normalize_name(i["name"]) == _normalize_name(resolved_name)), None
        )
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
                "recipe": recipe.title,
            })
    return missing


def consume_ingredients_for_recipe(recipe_id: int, user_id: int) -> dict:
    recipe = get_recipe(recipe_id, user_id)
    if not recipe:
        return {"success": False, "error": "Receta no encontrada"}

    inv = list_inventory(user_id)
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
        consumption_plan.append({"item_id": stock_item["id"], "consume_base": required_base, "unit": stock_item["unit"]})

    if missing:
        return {"success": False, "missing": missing}

    with _db() as db:
        for plan in consumption_plan:
            row = db.query(InventoryItemModel).filter(
                InventoryItemModel.id == plan["item_id"]
            ).first()
            if row:
                base_unit, base_qty = _to_base(float(row.quantity), row.unit)
                new_base_qty = round(base_qty - plan["consume_base"], 2)
                factor = UNIT_TO_BASE[_normalize_unit(row.unit)][1]
                row.quantity = round(new_base_qty / factor, 2)

    return {"success": True, "inventory": list_inventory(user_id)}


def list_low_stock_items(user_id: int) -> list:
    return [i for i in list_inventory(user_id) if _is_low_stock(i)]


def get_shopping_list(user_id: int) -> dict:
    inventory_items = list_inventory(user_id)
    low_stock = [i for i in inventory_items if _is_low_stock(i)]
    planned_recipes = list_recipes(user_id)
    planned_recipes = [r for r in planned_recipes if r.planned_to_cook]
    missing_for_planned = []
    for recipe in planned_recipes:
        missing_for_planned.extend(_compute_recipe_missing(recipe, inventory_items))
    return {
        "low_stock": low_stock,
        "planned_recipes": [r.model_dump() for r in planned_recipes],
        "missing_for_planned": missing_for_planned,
    }
