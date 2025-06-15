from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ingredients_recipe.views import RecipeViewSet, IngredientViewSet

recipe_router = DefaultRouter()
recipe_router.register('', RecipeViewSet, basename='recipes')

ingredient_router = DefaultRouter()
ingredient_router.register('', IngredientViewSet, basename='ingredients')
urlpatterns = [
    path('api/recipes/', include(recipe_router.urls)),
    path('api/ingredients/', include(ingredient_router.urls)),
]
