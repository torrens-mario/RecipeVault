from pydantic import BaseModel, Field
from typing import List


class Ingredient(BaseModel):
    name: str
    amount: str


class RecipeBase(BaseModel):
    title: str
    description: str = ""
    category: str = "General"
    servings: int = 2
    ingredients: List[Ingredient] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    favorite: bool = False
    image: str = ""
    planned_to_cook: bool = False
    prep_time: int = 0
    cook_time: int = 0
    difficulty: str = "Media"
    notes: str = ""
    rating: float = 0


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(RecipeBase):
    pass


class Recipe(RecipeBase):
    id: int
    is_public: bool = True


# ── Auth ───────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str
