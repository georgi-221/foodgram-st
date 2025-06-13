from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser




class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message=(
                    "Имя пользователя может содержать только буквы, "
                    "цифры и знаки @/./+/-/_"
                ),
                code="invalid_username",
            )
        ],
    )
    email = models.EmailField(unique=True)
    avatar = models.ImageField(
        upload_to='users/avatars/',
        default=None,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username


class Subscription(models.Model):
    following = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='user_followers'
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='user_subscriptions'
    )

    class Meta:
        ordering = ['user']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_user_following'
            )
        ]
