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
    display: Optional[str] = None
    title: Optional[str] = None
    originalText: Optional[str] = None
    referenceId: str


class RecipeInstruction(BaseModel):
    id: Optional[str] = None
    title: str = ""
    summary: str = ""
    text: str
    ingredientReferences: List[str] = Field(default_factory=list)


class RecipeSettings(BaseModel):
    public: Optional[bool] = False
    showNutrition: Optional[bool] = False
    showAssets: Optional[bool] = False
    landscapeView: Optional[bool] = False
    disableComments: Optional[bool] = False
    disableAmount: Optional[bool] = False
    locked: Optional[bool] = False


class RecipeData(BaseModel):
    id: Optional[str] = None
    userId: str
    householdId: str
    groupId: str
    name: str
    slug: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    recipeServings: Optional[float] = None
    recipeYieldQuantity: Optional[float] = None
    recipeYield: Optional[str] = None
    totalTime: Optional[str] = None
    prepTime: Optional[str] = None
    cookTime: Optional[str] = None
    performTime: Optional[str] = None
    recipeCategory: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    rating: Optional[int] = None
    orgURL: Optional[str] = None
    dateAdded: Optional[str] = None
    dateUpdated: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    lastMade: Optional[str] = None
    nutrition: Optional[RecipeNutrition] = None
    recipeIngredient: List[RecipeIngredient] = Field(default_factory=list)
    recipeInstructions: List[RecipeInstruction] = Field(default_factory=list)
    settings: Optional[RecipeSettings] = None
    assets: List = Field(default_factory=list)
    notes: List = Field(default_factory=list)
    extras: dict = Field(default_factory=dict)
    comments: List = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")  # Allow extra fields
