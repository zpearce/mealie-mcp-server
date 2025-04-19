from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RecipeNutrition(BaseModel):
    calories: Optional[str] = None
    carbohydrateContent: Optional[str] = None
    cholesterolContent: Optional[str] = None
    fatContent: Optional[str] = None
    fiberContent: Optional[str] = None
    proteinContent: Optional[str] = None
    saturatedFatContent: Optional[str] = None
    sodiumContent: Optional[str] = None
    sugarContent: Optional[str] = None
    transFatContent: Optional[str] = None
    unsaturatedFatContent: Optional[str] = None


class RecipeIngredient(BaseModel):
    quantity: Optional[float] = None
    unit: Optional[str] = None
    food: Optional[str] = None
    note: str
    isFood: bool = False
    disableAmount: bool = True
    referenceId: Optional[str] = None


class RecipeInstruction(BaseModel):
    id: Optional[str] = None
    title: str = ""
    summary: str = ""
    text: str


class RecipeSettings(BaseModel):
    public: Optional[bool] = False
    showNutrition: Optional[bool] = False
    showAssets: Optional[bool] = False
    landscapeView: Optional[bool] = False
    disableComments: Optional[bool] = False
    disableAmount: Optional[bool] = False
    locked: Optional[bool] = False


class RecipeData(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    recipeServings: Optional[float] = None
    recipeYieldQuantity: Optional[float] = None
    recipeYield: Optional[str] = None
    totalTime: Optional[str] = None
    prepTime: Optional[str] = None
    cookTime: Optional[str] = None
    performTime: Optional[str] = None
    recipeCategory: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)
    tools: Optional[List[str]] = Field(default_factory=list)
    rating: Optional[int] = None
    orgURL: Optional[str] = None
    nutrition: Optional[RecipeNutrition] = None
    recipeIngredient: Optional[List[RecipeIngredient]] = None
    recipeInstructions: Optional[List[RecipeInstruction]] = None
    settings: Optional[RecipeSettings] = None

    model_config = ConfigDict(extra="allow")  # Allow extra fields
