import random
import string

from django.contrib.auth import get_user_model
from django.db import models

from ingredients_recipe.models import Recipe

User = get_user_model()


class FavoriteUserRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorites')


class ShoppingCartUserRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='shopping_cart_recipe')


def six_string():
    return ''.join(random.choice(string.ascii_letters) for i in range(6))


class ShortLink(models.Model):
    id = models.CharField(max_length=6, primary_key=True, default=six_string, editable=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
