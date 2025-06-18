from django.contrib.auth import get_user_model
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=64)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=256)
    image = models.ImageField()
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()
    ingredients = models.ManyToManyField('Ingredient', through='RecipeIngredient', related_name='recipes')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='recipe_ingredients')
    amount = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['recipe', 'ingredient']
        verbose_name = 'Recipe Ingredient'
        verbose_name_plural = 'Recipe Ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.amount} of {self.ingredient} for {self.recipe}'
