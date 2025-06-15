from django.contrib import admin

from relations.models import FavoriteUserRecipe, ShoppingCartUserRecipe

admin.site.register(FavoriteUserRecipe)
admin.site.register(ShoppingCartUserRecipe)
