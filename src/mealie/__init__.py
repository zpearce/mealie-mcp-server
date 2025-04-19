from .client import MealieClient
from .recipe import RecipeMixin


class MealieFetcher(
    RecipeMixin,
    MealieClient,
):
    pass
