from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from djoser.views import UserViewSet
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django.core.files.base import ContentFile
import base64
import uuid
from django.shortcuts import get_object_or_404

from custom_user.models import Subscription
from custom_user.serializers import AvatarSerializer, BaseUserSerializer, UserSubscriptionSerializer
from ingredients_recipe.permissions import IsAuthorOrReadOnly

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        insts = [sub.to for sub in request.user.from_sender.select_related('to')]
        page = self.paginate_queryset(insts)
        if page:
            serializer = UserSubscriptionSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = UserSubscriptionSerializer(insts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe', permission_classes=[IsAuthorOrReadOnly])
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            return self._create(request, id)
        return self._remove(request, id)

    def _create(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)
        if request.user == target_user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        inst, created = Subscription.objects.get_or_create(from_source=request.user, to=target_user)
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(
            UserSubscriptionSerializer(target_user, context={'request': request}).data,
            status=status.HTTP_201_CREATED)

    def _remove(self, request, user_id):
        subscription = request.user.from_sender.filter(to_id=user_id)
        get_object_or_404(User, pk=user_id)
        if not subscription.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvatarRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self._get_user()).data)

    def update(self, request, *args, **kwargs):
        avatar = request.data.get('avatar')
        if not avatar:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self._convert(request.user, avatar)
        if request.user.avatar:
            return Response({'avatar': request.build_absolute_uri(request.user.avatar.url)})
        else:
            return Response({'avatar': None})

    def destroy(self, request, *args, **kwargs):
        if not request.user.avatar:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        request.user.avatar.delete()
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _convert(self, user, avatar_data):
        format, imgstr = avatar_data.split(';base64,')
        ext = format.split('/')[-1]
        user.avatar.save(
            f'{uuid.uuid4()}.{ext}',
            ContentFile(base64.b64decode(imgstr))
        )
        user.save()

    def _get_user(self):
        return self.request.user


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(BaseUserSerializer(request.user, context={'request': request}).data)
