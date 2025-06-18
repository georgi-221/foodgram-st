from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from ingredients_recipe.filters import RecipeFilter
from ingredients_recipe.models import Ingredient, Recipe
from ingredients_recipe.paginatior import RecipePagination
from ingredients_recipe.permissions import IsAuthorOrReadOnly
from ingredients_recipe.serializers import IngredientSerializer, RecipeListSerializer, RecipeWriteSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name', '')
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = RecipePagination
    serializer_class = RecipeListSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'get':
            return RecipeListSerializer
        return RecipeWriteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
