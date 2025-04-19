from .client import MealieClient
from .food import FoodMixin
from .mealplan import MealplanMixin
from .recipe import RecipeMixin
from .shopping_list import ShoppingListMixin


class MealieFetcher(
    FoodMixin,
    MealplanMixin,
    RecipeMixin,
    ShoppingListMixin,
    MealieClient,
):
    pass
