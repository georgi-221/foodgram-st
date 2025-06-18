from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status
from rest_framework.decorators import api_view
from ingredients_recipe.models import Recipe, RecipeIngredient
from relations.models import ShortLink, FavoriteUserRecipe, ShoppingCartUserRecipe
from rest_framework.response import Response
from django.db.models import Sum

from relations.serializers import ShortRecipeSerializer


@api_view(['GET'])
def redirect_short_link(request, pk):
    try:
        link_obj = ShortLink.objects.select_related('recipe').get(recipe_id=pk)
        return redirect('recipes-detail', pk=link_obj.id)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def generate_short_link(request, pk=None):
    link = ShortLink(recipe_id=pk)
    link.save()
    return Response({'short-link': reverse('short-link', kwargs={'pk': link.id})})


@api_view(['post', 'delete'])
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


@api_view(['post', 'delete'])
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


@api_view(['get'])
def download_shopping_cart(request):
    user = request.user

    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart_recipe__user=user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        total_amount=Sum('amount')
    ).order_by('ingredient__name')

    recipes = ShoppingCartUserRecipe.objects.filter(
        user=user
    ).values_list(
        'recipe__name', flat=True
    )

    data = {
        'ingredients': list(ingredients),
        'recipes': list(recipes),
        'message': 'Shopping list generated successfully'
    }

    return Response(data)
