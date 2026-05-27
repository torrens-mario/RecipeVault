from pydantic import BaseModel, EmailStr, Field
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
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
