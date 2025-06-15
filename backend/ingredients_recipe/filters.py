import django_filters

from ingredients_recipe.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.NumberFilter(method='filter_favorite')
    is_in_shopping_cart = django_filters.NumberFilter(method='filter_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author']

    def filter_favorite(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart_recipe__user=self.request.user)
        return queryset
