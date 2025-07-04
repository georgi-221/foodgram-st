from relations.views import generate_short_link, favorite, redirect_short_link, shopping_cart, download_shopping_cart
from django.urls import path

urlpatterns = [
    path('api/recipes/<int:pk>/get-link/', generate_short_link),
    path('api/recipes/<int:pk>/shopping_cart/', shopping_cart),
    path('api/recipes/<int:pk>/favorite/', favorite),
    path('api/recipes/download_shopping_cart/', download_shopping_cart),
    path('s/<str:pk>/', redirect_short_link, name='short-link')
]
