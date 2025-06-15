from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework.validators import UniqueValidator

from relations.serializers import ShortRecipeSerializer

User = get_user_model()


class UserCCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'password',
            'username',
            'first_name',
            'last_name'
        )


class BaseUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        abstract = True
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'username',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                user.from_sender.filter(to=obj).exists())


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)


class UserSubscriptionSerializer(BaseUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, user):
        queryset = user.recipes.all()
        limit = self._get_recipes_limit()
        if limit:
            queryset = queryset[:limit]
        return ShortRecipeSerializer(queryset, many=True, context=self.context).data

    def _get_recipes_limit(self):
        try:
            return int(self.context['request'].query_params.get('recipes_limit'))
        except Exception:
            return None
