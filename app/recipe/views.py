"""
views for recipe api
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    # view for managing recipe api

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()

    # the following two lines
    # will require the user to be authenticated
    # in order to interact with recipe api
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # override get_queryset
        # retrieve recipes for authenticated user

        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        # return the serializer class for request

        if self.action == 'list':
            # notice there's no () at the end
            # ...RecipeSerializer()
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        # create a new recipe

        serializer.save(user=self.request.user)
