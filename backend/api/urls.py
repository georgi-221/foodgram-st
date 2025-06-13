from django.urls import include, path
from rest_framework import routers

from users.views import CustomUserViewSet
from recipes.views import IngredientViewSet, RecipeViewSet

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')

def recipe_viewset_actions(actions):
    return RecipeViewSet.as_view(actions)

urlpatterns = [
    path('', include(router.urls)),

    path('recipes/', recipe_viewset_actions({'get': 'list', 'post': 'create'}), name='recipe-list'),
    path('recipes/<int:pk>/', recipe_viewset_actions({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='recipe-detail'),

    path('recipes/<int:pk>/favorite/', recipe_viewset_actions({
        'post': 'favorite',
        'delete': 'favorite',
    }), name='recipe-favorite'),

    path('recipes/<int:pk>/shopping_cart/', recipe_viewset_actions({
        'post': 'shopping_cart',
        'delete': 'shopping_cart',
    }), name='recipe-shopping-cart'),

    path('recipes/<int:pk>/get-link/', recipe_viewset_actions({
        'get': 'get_short_link',
    }), name='recipe-get-short-link'),

    path('recipes/download_shopping_cart/', recipe_viewset_actions({
        'get': 'download_shopping_cart',
    }), name='download-shopping-cart'),

    path('auth/', include('djoser.urls.authtoken')),
]
