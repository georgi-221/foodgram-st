import base64
import uuid
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from custom_user.serializers import BaseUserSerializer
from ingredients_recipe.models import Ingredient
from ingredients_recipe.models import Recipe, RecipeIngredient
from django.contrib.auth import get_user_model

from main.settings import MIN_COOKING_TIME, MAX_COOKING_TIME

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = BaseUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=recipe).exists()


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME)


class ImageField(serializers.Field):

    def to_internal_value(self, data):
        try:
            format_, imgstr = data.split(';base64,')
            ext = format_.split('/')[-1]
            return ContentFile(
                base64.b64decode(imgstr),
                name=f'{uuid.uuid4()}.{ext}'
            )
        except Exception:
            raise serializers.ValidationError('Неверный формат изображения')


class ImageSerializerField(serializers.Field):
    def to_internal_value(self, data):
        try:
            format_, imgstr = data.split(';base64,')
            ext = format_.split('/')[-1]
            return ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
        except:
            raise serializers.ValidationError('Некорректный формат изображения')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = ImageSerializerField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'image', 'name', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('')
        ingredient_ids = set()
        for ingredient in value:
            if not ingredient.get('id'):
                raise serializers.ValidationError('')
            if ingredient['id'] in ingredient_ids:
                raise serializers.ValidationError('')
            ingredient_ids.add(ingredient['id'])
        return value

    @transaction.atomic
    def create(self, validated_data):
        if 'ingredients' not in validated_data:
            raise serializers.ValidationError('')
        ingredients = validated_data.pop('ingredients')
        image = validated_data.pop('image')

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            image=image,
            **validated_data
        )
        self._save_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        if recipe.author != self.context['request'].user:
            raise PermissionDenied('Нельзя изменять чужие рецепты')

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is None:
            raise serializers.ValidationError('Укажите ингредиенты')

        recipe.recipe_ingredients.all().delete()
        self._save_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def _save_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data
