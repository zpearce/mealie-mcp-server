from .client import MealieClient
from .food import FoodMixin
from .recipe import RecipeMixin


class MealieFetcher(
    FoodMixin,
    RecipeMixin,
    MealieClient,
):
    pass
