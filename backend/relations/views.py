from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status

from ingredients_recipe.models import Recipe
from relations.models import ShortLink, FavoriteUserRecipe, ShoppingCartUserRecipe
from rest_framework.response import Response

from relations.serializers import ShortRecipeSerializer


def redirect_short_link(request, pk):
    try:
        link_obj = ShortLink.objects.select_related('recipe').get(recipe_id=pk)
        return redirect('recipes-detail', pk=link_obj.id)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def generate_short_link(request, pk=None):
    link = ShortLink.objects.create(recipe_id=pk)
    return Response({'short-link': reverse('short-link', kwargs={'pk': link.id})})


def favorite(request, pk=None):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user

    if not user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        _, created = FavoriteUserRecipe.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = ShortRecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    else:  # DELETE
        deleted = user.favorites.filter(recipe=recipe).delete()[0]
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


def shopping_cart(request, pk=None):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user

    if not user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        _, created = ShoppingCartUserRecipe.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = ShortRecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    else:
        deleted = user.shopping_cart.filter(recipe=recipe).delete()[0]
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
