from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from api.pagination import UserPagination
from .serializers import AvatarSerializer, SubscriptionUserSerializer
from .models import CustomUser, Subscription


class CustomUserViewSet(DjoserUserViewSet):
    pagination_class = UserPagination

    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()

    def perform_create(self, serializer, *args, **kwargs):
        data = serializer.validated_data
        required_fields = ('first_name', 'last_name')
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            raise serializers.ValidationError(
                {field: 'Это поле обязательно' for field in missing}
            )
        super().perform_create(serializer)

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {'avatar': 'Это поле обязательно'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = AvatarSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({'avatar': user.avatar.url}, status=status.HTTP_200_OK)

        if user.avatar:
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        followed_users = CustomUser.objects.filter(user_followers__user=user)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(followed_users, request=request)

        serializer = SubscriptionUserSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        user = request.user
        following = get_object_or_404(CustomUser, id=id)

        if user == following:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if Subscription.objects.filter(user=user, following=following).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, following=following)

            serializer = SubscriptionUserSerializer(
                following, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        deleted, _ = Subscription.objects.filter(user=user, following=following).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
