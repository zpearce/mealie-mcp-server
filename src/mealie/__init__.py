from .client import MealieClient
from .food import FoodMixin
from .mealplan import MealplanMixin
from .recipe import RecipeMixin


class MealieFetcher(
    FoodMixin,
    MealplanMixin,
    RecipeMixin,
    MealieClient,
):
    pass
