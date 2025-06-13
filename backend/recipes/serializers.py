from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from .models import Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('id',)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_amounts',
        many=True
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('id', 'author', 'is_favorited', 'is_in_shopping_cart')

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredient_amounts')
        recipe = Recipe.objects.create(**validated_data)
        self._set_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredient_amounts', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients_data is not None:
            instance.ingredient_amounts.all().delete()
            self._set_ingredients(instance, ingredients_data)

        return instance

    def _set_ingredients(self, recipe, ingredients_data):
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            ) for item in ingredients_data
        ])

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('У рецепта должна быть картинка')
        return value

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'У рецепта должен быть хотя бы один ингредиент'
            })

        seen_ingredients = set()
        for item in ingredients:
            ingr_id = item.get('id')
            if ingr_id in seen_ingredients:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты должны быть уникальными'
                })
            seen_ingredients.add(ingr_id)

            try:
                amount = int(item.get('amount'))
            except (TypeError, ValueError):
                raise serializers.ValidationError({
                    'ingredients': 'Количество ингредиента должно быть целым числом'
                })

            if amount <= 0:
                raise serializers.ValidationError({
                    'ingredients': 'Количество ингредиента должно быть больше нуля'
                })

        if self.instance is None:
            if not self.initial_data.get('image'):
                raise serializers.ValidationError({
                    'image': 'У рецепта должна быть картинка'
                })

        return data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = instance.image.url
        return representation
