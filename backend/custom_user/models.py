from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(null=True, blank=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    USERNAME_FIELD = 'email'


User = get_user_model()


class Subscription(models.Model):
    from_source = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_sender')
    to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_sender')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['from_source', 'to'], name='unique_sub')]
