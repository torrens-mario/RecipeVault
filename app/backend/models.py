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

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int
