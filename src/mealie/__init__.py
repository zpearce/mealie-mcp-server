from .client import MealieClient
from .food import FoodMixin
from .recipe import RecipeMixin
from .shopping_list import ShoppingListMixin


class MealieFetcher(
    FoodMixin,
    RecipeMixin,
    ShoppingListMixin,
    MealieClient,
):
    pass
