from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated, List


class Ingredient(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    amount: str = Field(default="", max_length=50)


class RecipeBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    category: str = Field(default="General", max_length=50)
    servings: int = Field(default=2, ge=1, le=100)
    ingredients: List[Ingredient] = Field(default_factory=list, max_length=100)
    steps: List[Annotated[str, Field(max_length=2000)]] = Field(default_factory=list, max_length=100)
    tags: List[Annotated[str, Field(max_length=50)]] = Field(default_factory=list, max_length=50)
    favorite: bool = False
    image: str = Field(default="", max_length=500)
    planned_to_cook: bool = False
    prep_time: int = Field(default=0, ge=0, le=1440)
    cook_time: int = Field(default=0, ge=0, le=1440)
    difficulty: str = Field(default="Media", max_length=20)
    notes: str = Field(default="", max_length=5000)
    rating: float = Field(default=0, ge=0, le=5)

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v not in ('Fácil', 'Media', 'Difícil'):
            raise ValueError('La dificultad debe ser Fácil, Media o Difícil')
        return v


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
