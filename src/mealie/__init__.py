from .client import MealieClient
from .group import GroupMixin
from .recipe import RecipeMixin
from .user import UserMixin


class MealieFetcher(
    RecipeMixin,
    UserMixin,
    GroupMixin,
    MealieClient,
):
    pass
